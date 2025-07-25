import json
from typing import AsyncGenerator
from google.adk.agents import BaseAgent, LlmAgent, ParallelAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai.types import Content, Part
from agentic_code_analyzer.agents.language_detection_agent import LanguageDetectionAgent
from agentic_code_analyzer.agents.region_tag_agent import RegionTagExtractionAgent
from agentic_code_analyzer.agents.product_id_agent import ProductIdentificationAgent
from agentic_code_analyzer.agents.analysis.code_quality_agent import CodeQualityAgent
from agentic_code_analyzer.agents.analysis.api_analysis_agent import ApiAnalysisAgent
from agentic_code_analyzer.agents.analysis.clarity_readability_agent import ClarityReadabilityAgent
from agentic_code_analyzer.agents.analysis.runnability_agent import RunnabilityAgent
from agentic_code_analyzer.evaluation_agent.evaluation_agent import EvaluationReviewAgent

class ResultProcessingAgent(BaseAgent):
    """Agent to process and structure the final output."""
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        try:
            product_info = ctx.session.state.get("product_identification_agent_output", "")
            if isinstance(product_info, str):
                product_name, product_category = product_info.split(",", 1) if "," in product_info else (product_info, "Unknown")
            else:
                product_name, product_category = "Unknown", "Unknown"

            analysis_output = {
                "language": ctx.session.state.get("language_detection_agent_output", "Unknown"),
                "product_name": product_name.strip(),
                "product_category": product_category.strip(),
                "region_tags": ctx.session.state.get("region_tag_extraction_agent_output", "").split(","),
                "analysis": {
                    "quality_summary": ctx.session.state.get("code_quality_agent_output", "Not available"),
                    "api_usage_summary": ctx.session.state.get("api_analysis_agent_output", "Not available"),
                    "best_practices_summary": ctx.session.state.get("clarity_readability_agent_output", "Not available"),
                    "runnability_summary": ctx.session.state.get("runnability_agent_output", "Not available"),
                },
                "evaluation": ctx.session.state.get("evaluation_review_agent_output", "Not available"),
            }
            
            final_json = json.dumps(analysis_output, indent=2)
            yield Event(
                author=self.name,
                content=Content(parts=[Part(text=final_json)]),
                turn_complete=True,
            )
        except (KeyError, TypeError) as e:
            yield Event(
                author=self.name,
                content=Content(parts=[Part(text=f"Error accessing agent results from session state: {e}")]),
                turn_complete=True,
            )
        except json.JSONDecodeError as e:
            yield Event(
                author=self.name,
                content=Content(parts=[Part(text=f"Error encoding final results to JSON: {e}")]),
                turn_complete=True,
            )
        except Exception as e:
            yield Event(
                author=self.name,
                content=Content(parts=[Part(text=f"An unexpected error occurred while processing final results: {e}")]),
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
                ProductIdentificationAgent(name="product_identification_agent", output_key="product_identification_agent_output"),
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

    def _create_evaluation_agent(self) -> EvaluationReviewAgent:
        """Creates the evaluation agent."""
        return EvaluationReviewAgent(name="evaluation_review_agent", output_key="evaluation_review_agent_output")

    def _create_result_processing_agent(self) -> ResultProcessingAgent:
        """Creates the result processing agent."""
        return ResultProcessingAgent(name="result_processor")
