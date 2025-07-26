import json
import os
import re
import pydantic
from typing import AsyncGenerator, List, Dict, Any
from google.adk.agents import BaseAgent, LlmAgent, ParallelAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai.types import Content, Part
from agentic_code_analyzer.models import (
    ClarityReadabilityOutput,
    CodeQualityOutput,
    EvaluationOutput,
    RunnabilityOutput,
)
from agentic_code_analyzer.agents.language_detection_agent import LanguageDetectionAgent
from agentic_code_analyzer.agents.region_tag_agent import RegionTagExtractionAgent
from agentic_code_analyzer.agents.product_categorization_agent import ProductCategorizationAgent
from agentic_code_analyzer.agents.analysis.code_quality_agent import CodeQualityAgent
from agentic_code_analyzer.agents.analysis.api_analysis_agent import ApiAnalysisAgent
from agentic_code_analyzer.agents.analysis.clarity_readability_agent import ClarityReadabilityAgent
from agentic_code_analyzer.agents.analysis.runnability_agent import RunnabilityAgent
from agentic_code_analyzer.agents.analysis.initial_analysis_agent import InitialAnalysisAgent
from agentic_code_analyzer.agents.analysis.json_formatting_agent import JsonFormattingAgent

class ResultProcessingAgent(BaseAgent):
    """
    An agent that processes the results of the analysis, enforces the single
    penalty rule, and formats them into a structured JSON object.

    This agent takes the raw output from the other agents in the system,
    deduplicates penalties according to a defined hierarchy, and then
    transforms the result into a clean, consistent, and easy-to-understand JSON
    object. It also handles errors and ensures that the final output is always a
    valid JSON object.
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
        based on a predefined hierarchy.
        """
        if "criteria_breakdown" not in evaluation_output:
            return evaluation_output

        # The hierarchy, from highest to lowest priority.
        hierarchy = [
            'runnability_and_configuration',
            'api_effectiveness_and_correctness',
            'language_best_practices',
            'formatting_and_consistency',
            'comments_and_code_clarity',
            'llm_training_fitness_and_explicitness'
        ]

        penalized_recommendations = set()

        # Sort criteria according to the hierarchy
        sorted_criteria = sorted(
            evaluation_output["criteria_breakdown"],
            key=lambda x: hierarchy.index(x.get("criterion_name")) if x.get("criterion_name") in hierarchy else len(hierarchy)
        )

        for criterion in sorted_criteria:
            if "recommendations_for_llm_fix" not in criterion:
                continue

            unique_recommendations = []
            for rec in criterion["recommendations_for_llm_fix"]:
                if rec not in penalized_recommendations:
                    unique_recommendations.append(rec)
                    penalized_recommendations.add(rec)

            # If recommendations were removed, we just update the list.
            criterion["recommendations_for_llm_fix"] = unique_recommendations

        evaluation_output["criteria_breakdown"] = sorted_criteria
        return evaluation_output

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Processes the results of the analysis and yields a final event with the
        structured JSON output.
        """
        def _to_dict(obj):
            if isinstance(obj, pydantic.BaseModel):
                return obj.model_dump()
            return obj

        try:
            # The evaluation_review_agent now produces the full structure
            evaluation_output = ctx.session.state.get("evaluation_review_agent_output", {})

            # Enforce the single penalty hierarchy to prevent double-penalizing.
            deduplicated_evaluation = self._enforce_single_penalty_hierarchy(evaluation_output)

            # Consolidate all final data into one object
            final_output = {
                "language": ctx.session.state.get("language_detection_agent_output", "Unknown"),
                "product_name": ctx.session.state.get("product_name", "Unknown"),
                "product_category": ctx.session.state.get("product_category", "Unknown"),
                "region_tags": ctx.session.state.get("region_tag_extraction_agent_output", "").split(","),
                "evaluation": deduplicated_evaluation
            }

            final_json = json.dumps(final_output, indent=2)

        except json.JSONDecodeError as e:
            final_json = json.dumps({"error": f"Failed to decode JSON in ResultProcessingAgent: {str(e)}"})
        except KeyError as e:
            final_json = json.dumps({"error": f"Missing expected key in session state: {str(e)}"})
        except Exception as e:
            final_json = json.dumps({"error": f"An unexpected error occurred in ResultProcessingAgent: {type(e).__name__} - {str(e)}"})

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
        # Step 1: An agent to perform the detailed analysis using tools (like search).
        # It does NOT have an output_schema, as that conflicts with using tools.
        # Its text output will be used by the next agent.
        initial_analysis_agent = InitialAnalysisAgent(
            name="initial_analysis_agent",
            output_key="initial_analysis_output", # Store raw text output here
            model=os.environ.get("GEMINI_PRO_MODEL", "gemini-1.5-pro-latest"),
        )

        # Step 2: An agent to format the raw text from the previous agent into the
        # required JSON structure. This agent has an output_schema but NO tools.
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
