"""
This module defines the main orchestrators for the Health Scoring Agent.

It contains the `CodeAnalyzerOrchestrator`, a sequential agent that coordinates
the entire code analysis workflow from initial detection to final output.
The orchestrator is the central component that drives the multi-agent system,
ensuring each specialized agent performs its task in the correct sequence.
"""

import json
import logging
import os
from typing import Any

from google.adk.agents import ParallelAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai.types import Content, Part

from agentic_code_analyzer.models import AnalysisResult
from agentic_code_analyzer.agents.deterministic_language_detection_agent import (
    DeterministicLanguageDetectionAgent,
)
from agentic_code_analyzer.agents.deterministic_region_tag_agent import (
    DeterministicRegionTagAgent,
)
from agentic_code_analyzer.agents.product_categorization_agent import (
    ProductCategorizationAgent,
)
from agentic_code_analyzer.agents.validation_agent import ValidationAgent
from agentic_code_analyzer.agents.code_cleaning_agent import CodeCleaningAgent
from agentic_code_analyzer.agents.analysis.initial_analysis_agent import (
    InitialAnalysisAgent,
)
from agentic_code_analyzer.agents.analysis.json_formatting_agent import (
    JsonFormattingAgent,
)

logger = logging.getLogger(__name__)


SUPPORTED_LANGUAGES: set[str] = {
    "C#",
    "C++",
    "Go",
    "Java",
    "Javascript",
    "PHP",
    "Python",
    "Ruby",
    "Rust",
    "Terraform",
}


class CodeAnalyzerOrchestrator(SequentialAgent):
    """
    Orchestrates the end-to-end code analysis workflow.

    This agent manages a sequence of sub-agents to perform a comprehensive
    analysis of a given code snippet. The workflow is designed for robustness
    and efficiency, with clear separation of concerns at each step:

    1.  **Initial Detection (Parallel):** The `initial_detection_agent` runs
        language and region tag detection concurrently for speed. This step
        gathers basic metadata without incurring LLM costs.

    2.  **Validation:** The `validation_agent` performs critical pre-checks. It
        ensures that region tags were found and that the detected language is
        supported. If validation fails, the entire workflow is halted early to
        avoid unnecessary processing.

    3.  **Code Cleaning:** The `code_cleaning_agent` removes all comments from
        the code. This standardizes the input for the analytical agents and
        ensures the evaluation is based purely on executable code.

    4.  **Product Categorization:** The `product_categorization_agent`
        identifies the Google Cloud product associated with the code, using a
        fast, rule-based approach with an LLM fallback for accuracy.

    5.  **Evaluation (Sequential):** The `evaluation_agent` is a two-step
        sub-workflow. First, a powerful LLM performs a detailed, qualitative
        analysis. Second, a faster LLM formats this analysis into a
        structured `AnalysisResult` object using the `output_schema` feature.

    6.  **Final Processing:** The orchestrator takes the structured output,
        combines it with metadata from earlier steps, and generates the final
        JSON output.
    """

    def __init__(self, **kwargs: Any):
        """
        Initializes the CodeAnalyzerOrchestrator and its sub-agents.

        Args:
            **kwargs: Keyword arguments passed to the parent `SequentialAgent`.
        """
        # Factory methods are used to construct the sub-agents.
        initial_detection_agent = self._create_initial_detection_agent()
        validation_agent = ValidationAgent(name="validation_agent")
        code_cleaning_agent = CodeCleaningAgent(name="code_cleaning_agent")
        product_categorization_agent = ProductCategorizationAgent(
            name="product_categorization_agent"
        )
        evaluation_agent = self._create_evaluation_agent()
        super().__init__(
            sub_agents=[
                initial_detection_agent,
                validation_agent,
                code_cleaning_agent,
                product_categorization_agent,
                evaluation_agent,
            ],
            **kwargs,
        )

    async def _process_final_event(
        self, event: Event, ctx: InvocationContext
    ) -> Event | None:
        """
        Processes the final event from the sub-agents to generate the final output.
        """
        logger.info(f"[{self.name}] Code analysis orchestration complete.")

        # If the workflow was halted by the validation agent, the final event will
        # contain the error. In this case, we simply forward the event.
        if event.author == "validation_agent":
            return event

        final_assessment = ctx.session.state.get("evaluation_review_agent_output")
        if not isinstance(final_assessment, AnalysisResult):
            logger.error("Assessment output was not of the expected type.")
            # Create a default error if the expected output is not found.
            error_response = json.dumps({"error": "Internal Server Error"})
            return Event(
                author=self.name,
                content=Content(parts=[Part(text=error_response)]),
                turn_complete=True,
            )

        final_output = {
            "language": ctx.session.state.get(
                "language_detection_agent_output", "Unknown"
            ),
            "product_name": ctx.session.state.get("product_name", "Unknown"),
            "product_category": ctx.session.state.get("product_category", "Unknown"),
            "region_tags": ctx.session.state.get(
                "region_tag_extraction_agent_output", ""
            ).split(","),
            "assessment": final_assessment.model_dump(),
        }
        final_json = json.dumps(final_output, indent=2)
        return Event(
            author=self.name,
            content=Content(parts=[Part(text=final_json)]),
            turn_complete=True,
        )

    def _create_initial_detection_agent(self) -> ParallelAgent:
        """
        Creates the parallel agent for the initial detection phase.

        This agent runs language detection and region tag extraction concurrently
        to save time.

        Returns:
            A `ParallelAgent` configured for initial detection tasks.
        """
        return ParallelAgent(
            name="initial_detection",
            sub_agents=[
                DeterministicLanguageDetectionAgent(name="language_detection_agent"),
                DeterministicRegionTagAgent(name="region_tag_extraction_agent"),
            ],
        )

    def _create_evaluation_agent(self) -> SequentialAgent:
        """
        Creates the sequential agent for the two-step evaluation process.

        This workflow consists of:
        1.  `InitialAnalysisAgent`: Performs a detailed, tool-based analysis
            of the code to generate a raw text review.
        2.  `JsonFormattingAgent`: Takes the raw review and structures it into a
            predefined JSON format.

        Returns:
            A `SequentialAgent` for the core evaluation workflow.
        """
        # This agent uses a more powerful model for the core analysis.
        initial_analysis_agent = InitialAnalysisAgent(
            name="initial_analysis_agent",
            output_key="initial_analysis_output",
            model=os.environ.get("GEMINI_PRO_MODEL", "gemini-2.5-pro"),
        )

        # This agent uses a faster, lighter model for the formatting task.
        json_formatting_agent = JsonFormattingAgent(
            name="json_formatting_agent",
            output_key="evaluation_review_agent_output",
            output_schema=AnalysisResult,
            model=os.environ.get("GEMINI_FLASH_LITE_MODEL", "gemini-2.5-flash-lite"),
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
        )
        return SequentialAgent(
            name="evaluation_workflow",
            sub_agents=[initial_analysis_agent, json_formatting_agent],
        )
