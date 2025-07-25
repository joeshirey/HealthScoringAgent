import json
import re
from typing import AsyncGenerator
from google.adk.agents import BaseAgent, LlmAgent, ParallelAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai.types import Content, Part
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
    """Agent to process and structure the final output."""
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        try:
            evaluation_output = ctx.session.state.get("evaluation_review_agent_output", "{}")
            if isinstance(evaluation_output, str):
                if '```json' in evaluation_output:
                    match = re.search(r'```json\s*([\s\S]*?)\s*```', evaluation_output)
                    if match:
                        evaluation_output = match.group(1)
                evaluation_data = json.loads(evaluation_output)
            else:
                evaluation_data = evaluation_output

            analysis_output = {
                "language": ctx.session.state.get("language_detection_agent_output", "Unknown"),
                "product_name": ctx.session.state.get("product_name", "Unknown"),
                "product_category": ctx.session.state.get("product_category", "Unknown"),
                "region_tags": ctx.session.state.get("region_tag_extraction_agent_output", "").split(","),
                "analysis": {
                    "quality_summary": json.loads(re.search(r'```json\s*([\s\S]*?)\s*```', ctx.session.state.get("code_quality_agent_output", "{}")).group(1)),
                    "api_usage_summary": json.loads(re.search(r'```json\s*([\s\S]*?)\s*```', ctx.session.state.get("api_analysis_agent_output", "{}")).group(1)),
                    "best_practices_summary": json.loads(re.search(r'```json\s*([\s\S]*?)\s*```', ctx.session.state.get("clarity_readability_agent_output", "{}")).group(1)),
                    "runnability_summary": json.loads(re.search(r'```json\s*([\s\S]*?)\s*```', ctx.session.state.get("runnability_agent_output", "{}")).group(1)),
                },
                "evaluation": evaluation_data,
            }
            
            final_json = json.dumps(analysis_output, indent=2)
        except (KeyError, TypeError, json.JSONDecodeError) as e:
            final_json = json.dumps({"error": f"Error in ResultProcessingAgent: {str(e)}"})
        
        yield Event(
            author=self.name,
            content=Content(parts=[Part(text=final_json)]),
            turn_complete=True,
        )

class CodeAnalyzerOrchestrator(SequentialAgent):
    """Orchestrates the code analysis workflow using parallel and sequential agents."""

    def __init__(self, **kwargs):
        initial_analysis_agent = self._create_initial_analysis_agent()
        code_analysis_agent = self._create_code_analysis_agent()
        evaluation_agent = self._create_evaluation_agent()
        result_processor = self._create_result_processing_agent()

        super().__init__(
            name=kwargs.get("name", "code_analyzer_orchestrator"),
            sub_agents=[
                initial_analysis_agent,
                code_analysis_agent,
                evaluation_agent,
                result_processor,
            ],
        )

    def _create_initial_analysis_agent(self) -> ParallelAgent:
        """Creates the parallel agent for the initial analysis phase."""
        return ParallelAgent(
            name="initial_analysis",
            sub_agents=[
                LanguageDetectionAgent(name="language_detection_agent", output_key="language_detection_agent_output"),
                RegionTagExtractionAgent(name="region_tag_extraction_agent", output_key="region_tag_extraction_agent_output"),
                ProductCategorizationAgent(name="product_categorization_agent"),
            ],
        )

    def _create_code_analysis_agent(self) -> ParallelAgent:
        """Creates the parallel agent for the code analysis phase."""
        return ParallelAgent(
            name="code_analysis",
            sub_agents=[
                CodeQualityAgent(name="code_quality_agent", output_key="code_quality_agent_output"),
                ApiAnalysisAgent(name="api_analysis_agent", output_key="api_analysis_agent_output"),
                ClarityReadabilityAgent(name="clarity_readability_agent", output_key="clarity_readability_agent_output"),
                RunnabilityAgent(name="runnability_agent", output_key="runnability_agent_output"),
            ],
        )

    def _create_evaluation_agent(self) -> SequentialAgent:
        """Creates the sequential agent for the two-step evaluation process."""
        initial_analysis_agent = InitialAnalysisAgent(
            name="initial_analysis_agent",
            output_key="initial_analysis_output",
            model="gemini-1.5-pro-latest",
        )
        json_formatting_agent = JsonFormattingAgent(
            name="json_formatting_agent",
            output_key="evaluation_review_agent_output",
            model="gemini-1.5-pro-latest",
        )
        return SequentialAgent(
            name="evaluation_workflow",
            sub_agents=[initial_analysis_agent, json_formatting_agent],
        )

    def _create_result_processing_agent(self) -> ResultProcessingAgent:
        """Creates the result processing agent."""
        return ResultProcessingAgent(name="result_processor")

