"""
This module defines the main orchestrator for the Health Scoring Agent.

It contains the `CodeAnalyzerOrchestrator`, a sequential agent that coordinates
the entire code analysis workflow, and the `ResultProcessingAgent`, which
finalizes the analysis output.
"""

import json
import logging
import os
import re
from typing import AsyncGenerator, Dict, Any, List, Set

import demjson3

from google.adk.agents import BaseAgent, ParallelAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai.types import Content, Part

from agentic_code_analyzer.models import EvaluationOutput
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


SUPPORTED_LANGUAGES: List[str] = [
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
]


class ResultProcessingAgent(BaseAgent):
    """
    Processes, cleans, and formats the final analysis output.

    This agent takes the raw output from the evaluation workflow, applies
    business logic such as the "single penalty rule," and combines it with
    metadata from other agents to produce the final, structured JSON response.
    """

    def _safe_json_load(self, data: Any) -> Dict[str, Any]:
        """
        Safely loads a JSON string into a dictionary.

        This method handles cases where the input is already a dictionary, a
        plain JSON string, or a JSON object embedded in a Markdown code block.
        It uses a lenient parser (`demjson3`) as a fallback.

        Args:
            data: The input data, which can be a dict, a JSON string, or a
                string containing a JSON object in a markdown block.

        Returns:
            A dictionary representing the loaded JSON, or an empty dictionary
            if parsing fails.
        """
        if isinstance(data, dict):
            return data
        if not isinstance(data, str):
            return {}

        json_string = data
        try:
            # Regex to find a JSON object within a markdown code block.
            match = re.search(
                r"```(json)?\s*({[\s\S]*?})\s*```", json_string, re.IGNORECASE
            )
            if match:
                json_string = match.group(2)

            # Attempt to parse with the standard json library first.
            return json.loads(json_string)
        except json.JSONDecodeError:
            # If standard parsing fails, fall back to the more lenient demjson3.
            try:
                decoded = demjson3.decode(json_string)
                if isinstance(decoded, dict):
                    return decoded
                return {}
            except demjson3.JSONDecodeError:
                # If all parsing attempts fail, return an empty dict.
                return {}
        except AttributeError:
            # This can happen if the input data is not a string-like object.
            return {}

    def _enforce_single_penalty_hierarchy(
        self, assessment_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enforces the single penalty rule on evaluation criteria.

        This rule ensures that a specific recommendation is only applied once,
        based on a predefined hierarchy of importance. For example, if a
        recommendation appears in both "runnability" and "code_clarity", it
        will only be kept in "runnability" (the higher-priority criterion).

        Args:
            assessment_output: The dictionary containing the analysis results,
                expected to have a 'criteria_breakdown' key.

        Returns:
            The evaluation output with duplicate recommendations removed
            according to the hierarchy.
        """
        if (
            not isinstance(assessment_output, dict)
            or "criteria_breakdown" not in assessment_output
        ):
            return assessment_output

        criteria_breakdown = assessment_output.get("criteria_breakdown")
        if not isinstance(criteria_breakdown, list):
            return assessment_output

        # The hierarchy defines the order of importance for criteria.
        hierarchy: List[str] = [
            "runnability_and_configuration",
            "api_effectiveness_and_correctness",
            "language_best_practices",
            "formatting_and_consistency",
            "comments_and_code_clarity",
            "llm_training_fitness_and_explicitness",
        ]
        penalized_recommendations: Set[str] = set()

        def get_sort_key(criterion: Any) -> int:
            """Provides a sort key based on the hierarchy list."""
            if isinstance(criterion, dict):
                name = criterion.get("criterion_name")
                if name in hierarchy:
                    return hierarchy.index(name)
            return len(hierarchy)  # Place unknown criteria at the end.

        # Filter out any malformed (non-dict) items before sorting.
        valid_criteria = [c for c in criteria_breakdown if isinstance(c, dict)]
        sorted_criteria = sorted(valid_criteria, key=get_sort_key)

        processed_criteria: List[Dict[str, Any]] = []
        for criterion in sorted_criteria:
            recommendations = criterion.get("recommendations_for_llm_fix")
            if not isinstance(recommendations, list):
                # If recommendations are malformed, clear them but keep the criterion.
                criterion["recommendations_for_llm_fix"] = []
                processed_criteria.append(criterion)
                continue

            # Filter out recommendations that have already been penalized.
            unique_recommendations: List[str] = []
            for rec in recommendations:
                if not isinstance(rec, str):
                    continue  # Ignore malformed recommendations.
                if rec not in penalized_recommendations:
                    unique_recommendations.append(rec)
                    penalized_recommendations.add(rec)

            criterion["recommendations_for_llm_fix"] = unique_recommendations
            processed_criteria.append(criterion)

        assessment_output["criteria_breakdown"] = processed_criteria
        return assessment_output

    def _deduplicate_criteria(
        self, assessment_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        if (
            not isinstance(assessment_output, dict)
            or "criteria_breakdown" not in assessment_output
        ):
            return assessment_output

        criteria_breakdown = assessment_output.get("criteria_breakdown")
        if not isinstance(criteria_breakdown, list):
            return assessment_output

        unique_criteria: List[Dict[str, Any]] = []
        seen_criteria_names: Set[str] = set()

        for criterion in criteria_breakdown:
            if not isinstance(criterion, dict):
                continue  # Skip malformed entries

            criterion_name = criterion.get("criterion_name")
            if criterion_name and criterion_name not in seen_criteria_names:
                unique_criteria.append(criterion)
                seen_criteria_names.add(criterion_name)

        assessment_output["criteria_breakdown"] = unique_criteria
        return assessment_output

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Executes the result processing logic.

        This method retrieves the raw evaluation output from the session state,
        processes it, and yields a final event containing the structured JSON
        output.

        Args:
            ctx: The invocation context for the current agent run.

        Yields:
            A final `Event` containing the complete and formatted JSON analysis.
        """
        logger.info(f"[{self.name}] Starting result processing.")
        try:
            # Retrieve the raw output from the JSON formatting agent.
            raw_assessment_output = ctx.session.state.get(
                "evaluation_review_agent_output", "{}"
            )
            logger.debug(f"[{self.name}] Raw evaluation output received.")

            # Safely parse the JSON output.
            processed_output = self._safe_json_load(raw_assessment_output)
            logger.debug(f"[{self.name}] Safely loaded JSON output.")

            deduplicated_criteria = self._deduplicate_criteria(processed_output)
            logger.debug(f"[{self.name}] Deduplicated criteria.")

            # Apply the single penalty rule to deduplicate recommendations.
            deduplicated_assessment = self._enforce_single_penalty_hierarchy(
                deduplicated_criteria
            )
            logger.debug(f"[{self.name}] Enforced single penalty hierarchy.")

            # Combine all data points into the final output structure.
            final_output = {
                "language": ctx.session.state.get(
                    "language_detection_agent_output", "Unknown"
                ),
                "product_name": ctx.session.state.get("product_name", "Unknown"),
                "product_category": ctx.session.state.get(
                    "product_category", "Unknown"
                ),
                "region_tags": ctx.session.state.get(
                    "region_tag_extraction_agent_output", ""
                ).split(","),
                "assessment": deduplicated_assessment,
            }

            final_json = json.dumps(final_output, indent=2)
            logger.info(f"[{self.name}] Successfully created final JSON output.")

        except Exception as e:
            # In case of any unexpected error, create an error response.
            logger.error(
                f"[{self.name}] An unexpected error occurred: {e}", exc_info=True
            )
            error_message = (
                f"An unexpected error occurred in ResultProcessingAgent: "
                f"{type(e).__name__} - {str(e)}"
            )
            final_json = json.dumps({"error": error_message})

        # Yield the final result as a turn-complete event.
        yield Event(
            author=self.name,
            content=Content(parts=[Part(text=final_json)]),
            turn_complete=True,
        )


class CodeAnalyzerOrchestrator(BaseAgent):
    """
    Orchestrates the end-to-end code analysis workflow.

    This agent manages a sequence of sub-agents to perform a comprehensive
    analysis of a given code snippet. The workflow is as follows:
    1.  **Initial Detection:** Language and region tags are detected in parallel.

    2.  **Validation:** Validates the language and region tags, halting on failure.
    3.  **Code Cleaning:** Comments are removed from the code.
    4.  **Product Categorization:** The relevant product is identified.
    5.  **Evaluation:** A two-step process involving a detailed analysis
        followed by JSON formatting.
    6.  **Result Processing:** The final output is assembled and cleaned.
    """

    initial_detection_agent: ParallelAgent
    validation_agent: ValidationAgent
    code_cleaning_agent: CodeCleaningAgent
    product_categorization_agent: ProductCategorizationAgent
    evaluation_agent: SequentialAgent
    result_processor: ResultProcessingAgent

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
        result_processor = self._create_result_processing_agent()
        super().__init__(
            initial_detection_agent=initial_detection_agent,
            validation_agent=validation_agent,
            code_cleaning_agent=code_cleaning_agent,
            product_categorization_agent=product_categorization_agent,
            evaluation_agent=evaluation_agent,
            result_processor=result_processor,
            **kwargs,
        )

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Manually orchestrates the code analysis workflow to allow for
        conditional halting based on validation.
        """
        logger.info(f"[{self.name}] Starting code analysis orchestration.")

        # Step 1: Initial Detection (Parallel)
        async for event in self.initial_detection_agent.run_async(ctx):
            yield event
        logger.info(f"[{self.name}] Initial detection phase complete.")

        # Step 2: Validation
        # The validation agent only yields an event if validation fails.
        async for event in self.validation_agent.run_async(ctx):
            # The only events yielded are final failure events.
            logger.warning(f"[{self.name}] Validation failed. Halting workflow.")
            yield event
            return

        logger.info(f"[{self.name}] Validation passed. Continuing workflow.")

        # Step 3: Code Cleaning
        async for event in self.code_cleaning_agent.run_async(ctx):
            yield event
        logger.info(f"[{self.name}] Code cleaning complete.")

        # Step 4: Product Categorization
        async for event in self.product_categorization_agent.run_async(ctx):
            yield event
        logger.info(f"[{self.name}] Product categorization complete.")

        # Step 5: Evaluation
        async for event in self.evaluation_agent.run_async(ctx):
            yield event
        logger.info(f"[{self.name}] Evaluation workflow complete.")

        # Step 6: Final Result Processing
        async for event in self.result_processor.run_async(ctx):
            yield event
        logger.info(f"[{self.name}] Result processing complete.")

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
            output_schema=EvaluationOutput,
            model=os.environ.get("GEMINI_FLASH_LITE_MODEL", "gemini-2.5-flash-lite"),
        )
        return SequentialAgent(
            name="evaluation_workflow",
            sub_agents=[initial_analysis_agent, json_formatting_agent],
        )

    def _create_result_processing_agent(self) -> ResultProcessingAgent:
        """
        Creates the agent responsible for final result processing.

        Returns:
            An instance of `ResultProcessingAgent`.
        """
        return ResultProcessingAgent(name="result_processor")
