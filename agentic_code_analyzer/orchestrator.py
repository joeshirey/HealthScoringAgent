import json
import os
import re
from typing import AsyncGenerator, Dict, Any

from google.adk.agents import BaseAgent, ParallelAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai.types import Content, Part

from agentic_code_analyzer.models import EvaluationOutput
from agentic_code_analyzer.agents.language_detection_agent import LanguageDetectionAgent
from agentic_code_analyzer.agents.region_tag_agent import RegionTagExtractionAgent
from agentic_code_analyzer.agents.product_categorization_agent import ProductCategorizationAgent
from agentic_code_analyzer.agents.analysis.initial_analysis_agent import InitialAnalysisAgent
from agentic_code_analyzer.agents.analysis.json_formatting_agent import JsonFormattingAgent


class ResultProcessingAgent(BaseAgent):
    """
    An agent that processes the results of the analysis, enforces the single
    penalty rule, and formats them into a structured JSON object.
    """
    def _safe_json_load(self, json_string: str) -> dict:
        """
        Safely loads a JSON string, extracting from markdown if necessary.
        """
        try:
            if '```json' in json_string:
                match = re.search(r'```json\s*([\s\S]*?)\s*```', json_string)
                if match:
                    json_string = match.group(1)
            return json.loads(json_string)
        except (json.JSONDecodeError, AttributeError):
            return {}

    def _enforce_single_penalty_hierarchy(self, evaluation_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforces the single penalty rule by removing duplicate recommendations
        based on a predefined hierarchy. This method is designed to be robust
        against malformed input from the LLM.
        """
        if not isinstance(evaluation_output, dict) or "criteria_breakdown" not in evaluation_output:
            return evaluation_output

        if not isinstance(evaluation_output.get("criteria_breakdown"), list):
            return evaluation_output

        hierarchy = [
            'runnability_and_configuration',
            'api_effectiveness_and_correctness',
            'language_best_practices',
            'formatting_and_consistency',
            'comments_and_code_clarity',
            'llm_training_fitness_and_explicitness'
        ]
        penalized_recommendations = set()

        def get_sort_key(criterion: Any) -> int:
            """Safely get the sort key for a criterion."""
            if isinstance(criterion, dict):
                name = criterion.get("criterion_name")
                if name in hierarchy:
                    return hierarchy.index(name)
            return len(hierarchy)

        sorted_criteria = sorted(
            evaluation_output["criteria_breakdown"],
            key=get_sort_key
        )

        for criterion in sorted_criteria:
            if not isinstance(criterion, dict) or not isinstance(criterion.get("recommendations_for_llm_fix"), list):
                continue

            unique_recommendations = []
            for rec in criterion["recommendations_for_llm_fix"]:
                if rec not in penalized_recommendations:
                    unique_recommendations.append(rec)
                    penalized_recommendations.add(rec)
            criterion["recommendations_for_llm_fix"] = unique_recommendations

        evaluation_output["criteria_breakdown"] = sorted_criteria
        return evaluation_output

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Processes the results of the analysis and yields a final event with the
        structured JSON output.
        """
        try:
            evaluation_output = ctx.session.state.get("evaluation_review_agent_output", {})

            # Convert Pydantic model to dict for processing, if it is one,
            # without directly importing pydantic.
            if hasattr(evaluation_output, 'model_dump'):
                processed_output = evaluation_output.model_dump()
            else:
                # Assume it's already a dict or something that can be processed.
                processed_output = evaluation_output

            deduplicated_evaluation = self._enforce_single_penalty_hierarchy(processed_output)

            final_output = {
                "language": ctx.session.state.get("language_detection_agent_output", "Unknown"),
                "product_name": ctx.session.state.get("product_name", "Unknown"),
                "product_category": ctx.session.state.get("product_category", "Unknown"),
                "region_tags": ctx.session.state.get("region_tag_extraction_agent_output", "").split(","),
                "evaluation": deduplicated_evaluation
            }

            final_json = json.dumps(final_output, indent=2)

        except Exception as e:
            final_json = json.dumps({
                "error": f"An unexpected error occurred in ResultProcessingAgent: {type(e).__name__} - {str(e)}",
            })

        yield Event(
            author=self.name,
            content=Content(parts=[Part(text=final_json)]),
            turn_complete=True,
        )


class CodeAnalyzerOrchestrator(SequentialAgent):
    """
    Orchestrates the code analysis workflow using a sequence of parallel and
    sequential agents.
    """

    def __init__(self, **kwargs):
        """
        Initializes the CodeAnalyzerOrchestrator.
        """
        initial_analysis_agent = self._create_initial_analysis_agent()
        evaluation_agent = self._create_evaluation_agent()
        result_processor = self._create_result_processing_agent()

        super().__init__(
            name=kwargs.get("name", "code_analyzer_orchestrator"),
            sub_agents=[
                initial_analysis_agent,
                evaluation_agent,
                result_processor,
            ],
        )

    def _create_initial_analysis_agent(self) -> ParallelAgent:
        """
        Creates the parallel agent for the initial analysis phase.
        """
        return ParallelAgent(
            name="initial_analysis",
            sub_agents=[
                LanguageDetectionAgent(name="language_detection_agent", output_key="language_detection_agent_output", model=os.environ.get("GEMINI_FLASH_LITE_MODEL", "gemini-1.5-flash-latest")),
                RegionTagExtractionAgent(name="region_tag_extraction_agent", output_key="region_tag_extraction_agent_output", model=os.environ.get("GEMINI_FLASH_LITE_MODEL", "gemini-1.5-flash-latest")),
                ProductCategorizationAgent(name="product_categorization_agent"),
            ],
        )

    def _create_evaluation_agent(self) -> SequentialAgent:
        """
        Creates the sequential agent for the two-step evaluation process.
        It first runs an analysis agent that uses tools to generate a detailed
        review, then a formatting agent to structure the output into JSON.
        """
        initial_analysis_agent = InitialAnalysisAgent(
            name="initial_analysis_agent",
            output_key="initial_analysis_output",
            model=os.environ.get("GEMINI_PRO_MODEL", "gemini-1.5-pro-latest"),
        )

        json_formatting_agent = JsonFormattingAgent(
            name="json_formatting_agent",
            output_key="evaluation_review_agent_output",
            output_schema=EvaluationOutput,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            model=os.environ.get("GEMINI_FLASH_LITE_MODEL", "gemini-1.5-flash-latest"),
        )
        return SequentialAgent(
            name="evaluation_workflow",
            sub_agents=[initial_analysis_agent, json_formatting_agent],
        )

    def _create_result_processing_agent(self) -> ResultProcessingAgent:
        """
        Creates the result processing agent.
        """
        return ResultProcessingAgent(name="result_processor")
