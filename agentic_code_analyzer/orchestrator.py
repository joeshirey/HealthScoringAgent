import json
import os
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
    """
    An agent that processes the results of the analysis and formats them into a
    structured JSON object.

    This agent takes the raw output from the other agents in the system and
    transforms it into a clean, consistent, and easy-to-understand JSON object.
    It also handles errors and ensures that the final output is always a valid
    JSON object.
    """
    def _safe_json_load(self, json_string: str) -> dict:
        """
        Safely loads a JSON string, extracting from markdown if necessary.

        This function takes a string as input and tries to parse it as JSON. It
        can handle strings that are wrapped in markdown code blocks, and it will
        return an empty dictionary if the string is not valid JSON.

        Args:
            json_string: The string to parse as JSON.

        Returns:
            A dictionary representing the parsed JSON, or an empty dictionary if
            the string is not valid JSON.
        """
        try:
            if '```json' in json_string:
                match = re.search(r'```json\s*([\s\S]*?)\s*```', json_string)
                if match:
                    json_string = match.group(1)
            return json.loads(json_string)
        except (json.JSONDecodeError, AttributeError):
            return {}

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Processes the results of the analysis and yields a final event with the
        structured JSON output.

        This method retrieves the output from the other agents in the system,
        formats it into a structured JSON object, and then yields a final event
        with the JSON object as its content.

        Args:
            ctx: The invocation context for the agent.

        Yields:
            A final event with the structured JSON output.
        """
        try:
            evaluation_output = ctx.session.state.get("evaluation_review_agent_output", "{}")
            evaluation_data = self._safe_json_load(evaluation_output)

            analysis_output = {
                "language": ctx.session.state.get("language_detection_agent_output", "Unknown"),
                "product_name": ctx.session.state.get("product_name", "Unknown"),
                "product_category": ctx.session.state.get("product_category", "Unknown"),
                "region_tags": ctx.session.state.get("region_tag_extraction_agent_output", "").split(","),
                "analysis": {
                    "quality_summary": self._safe_json_load(ctx.session.state.get("code_quality_agent_output", "{}")),
                    "api_usage_summary": self._safe_json_load(ctx.session.state.get("api_analysis_agent_output", "{}")),
                    "best_practices_summary": self._safe_json_load(ctx.session.state.get("clarity_readability_agent_output", "{}")),
                    "runnability_summary": self._safe_json_load(ctx.session.state.get("runnability_agent_output", "{}")),
                },
                "evaluation": evaluation_data,
            }
            
            final_json = json.dumps(analysis_output, indent=2)
        except Exception as e:
            final_json = json.dumps({"error": f"An unexpected error occurred in ResultProcessingAgent: {str(e)}"})
        
        yield Event(
            author=self.name,
            content=Content(parts=[Part(text=final_json)]),
            turn_complete=True,
        )

class CodeAnalyzerOrchestrator(SequentialAgent):
    """
    Orchestrates the code analysis workflow using a sequence of parallel and
    sequential agents.

    This agent is the main entry point for the code analysis workflow. It
    initializes and runs a sequence of other agents, each of which is
    responsible for a specific part of the analysis. The workflow is divided
    into three main phases: initial analysis, code analysis, and evaluation.
    """

    def __init__(self, **kwargs):
        """
        Initializes the CodeAnalyzerOrchestrator.

        This method creates the sub-agents that make up the code analysis
        workflow and then initializes the `SequentialAgent` with the sub-agents.
        """
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
        """
        Creates the parallel agent for the initial analysis phase.

        This agent is responsible for performing the initial analysis of the code,
        which includes detecting the language, extracting region tags, and
        categorizing the product.

        It is recommended to use the Gemini Flash model for these tasks, as they
        are relatively simple and do not require the more advanced capabilities
        of the Gemini Pro model.

        Returns:
            A `ParallelAgent` that runs the initial analysis agents in parallel.
        """
        return ParallelAgent(
            name="initial_analysis",
            sub_agents=[
                LanguageDetectionAgent(name="language_detection_agent", output_key="language_detection_agent_output", model=os.environ.get("GEMINI_FLASH_MODEL", "gemini-1.5-flash-latest")),
                RegionTagExtractionAgent(name="region_tag_extraction_agent", output_key="region_tag_extraction_agent_output", model=os.environ.get("GEMINI_FLASH_MODEL", "gemini-1.5-flash-latest")),
                ProductCategorizationAgent(name="product_categorization_agent"),
            ],
        )

    def _create_code_analysis_agent(self) -> ParallelAgent:
        """
        Creates the parallel agent for the code analysis phase.

        This agent is responsible for performing the main analysis of the code,
        which includes assessing code quality, API usage, clarity and
        readability, and runnability.

        It is recommended to use the Gemini Flash model for these tasks, as they
        are relatively simple and do not require the more advanced capabilities
        of the Gemini Pro model.

        Returns:
            A `ParallelAgent` that runs the code analysis agents in parallel.
        """
        return ParallelAgent(
            name="code_analysis",
            sub_agents=[
                CodeQualityAgent(name="code_quality_agent", output_key="code_quality_agent_output", model=os.environ.get("GEMINI_FLASH_MODEL", "gemini-1.5-flash-latest")),
                ApiAnalysisAgent(name="api_analysis_agent", output_key="api_analysis_agent_output", model=os.environ.get("GEMINI_FLASH_MODEL", "gemini-1.5-flash-latest")),
                ClarityReadabilityAgent(name="clarity_readability_agent", output_key="clarity_readability_agent_output", model=os.environ.get("GEMINI_FLASH_MODEL", "gemini-1.5-flash-latest")),
                RunnabilityAgent(name="runnability_agent", output_key="runnability_agent_output", model=os.environ.get("GEMINI_FLASH_MODEL", "gemini-1.5-flash-latest")),
            ],
        )

    def _create_evaluation_agent(self) -> SequentialAgent:
        """
        Creates the sequential agent for the two-step evaluation process.

        This agent is responsible for performing the final evaluation of the code.
        It first runs an initial analysis agent to get a detailed analysis of the
        code, and then it runs a JSON formatting agent to format the analysis
        into a clean, structured JSON object.

        It is recommended to use the Gemini Pro model for the initial analysis,
        as it is a more complex task that requires a deeper understanding of the
        code. It is recommended to use the Gemini Flash model for the JSON
        formatting, as it is a relatively simple task that does not require the
        more advanced capabilities of the Gemini Pro model.

        Returns:
            A `SequentialAgent` that runs the evaluation agents in sequence.
        """
        initial_analysis_agent = InitialAnalysisAgent(
            name="initial_analysis_agent",
            output_key="initial_analysis_output",
            model=os.environ.get("GEMINI_PRO_MODEL", "gemini-1.5-pro-latest"),
        )
        json_formatting_agent = JsonFormattingAgent(
            name="json_formatting_agent",
            output_key="evaluation_review_agent_output",
            model=os.environ.get("GEMINI_FLASH_MODEL", "gemini-1.5-flash-latest"),
        )
        return SequentialAgent(
            name="evaluation_workflow",
            sub_agents=[initial_analysis_agent, json_formatting_agent],
        )

    def _create_result_processing_agent(self) -> ResultProcessingAgent:
        """
        Creates the result processing agent.

        This agent is responsible for taking the raw output from the other agents
        in the system and transforming it into a clean, consistent, and
        easy-to-understand JSON object.

        Returns:
            A `ResultProcessingAgent` that processes the final results.
        """
        return ResultProcessingAgent(name="result_processor")
