"""
This module defines the agents responsible for the validation workflow.

This includes the `ValidationOrchestrator` and its sub-agents, which are
designed to verify the accuracy of an initial code analysis.
"""

import json
import os
from typing import Any

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools import google_search
from google.genai.types import Content

from agentic_code_analyzer.validation_model import EvaluationValidationOutput
from agentic_code_analyzer.agents.shared_config import GENERATE_CONTENT_CONFIG


class EvaluationVerificationAgent(LlmAgent):
    """
    Performs the first step of the validation workflow.

    This agent uses Google Search to fact-check the claims made in the original
    evaluation and produces a raw text analysis of its findings.
    """

    instruction: str

    def __init__(self, **kwargs: Any):
        """
        Initializes the EvaluationVerificationAgent.

        Args:
            **kwargs: Keyword arguments passed to the parent `LlmAgent`.
        """
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "prompts",
            "evaluation_validation_prompt.md",
        )
        with open(prompt_path, "r") as f:
            instruction = f.read()

        super().__init__(
            instruction=instruction,
            tools=[google_search],
            generate_content_config=GENERATE_CONTENT_CONFIG,
            **kwargs,
        )

    def _build_prompt(self, ctx: InvocationContext) -> Content:
        """
        Builds the prompt for the LLM by injecting the code and evaluation
        from the session state into the instruction template.
        """
        code_snippet = ctx.session.state.get("code_snippet", "")
        evaluation_json = ctx.session.state.get("evaluation_json", {})

        # Create a pretty-printed JSON string for the prompt.
        evaluation_str = json.dumps(evaluation_json, indent=2)

        # Replace placeholders in the instruction template.
        prompt_text = self.instruction.replace("{{code_snippet}}", code_snippet)
        prompt_text = prompt_text.replace("{{evaluation_json}}", evaluation_str)

        # The final prompt is just the formatted text.
        return Content.from_parts(prompt_text)


class ValidationFormattingAgent(LlmAgent):
    """
    Formats the raw validation text into a structured JSON object.

    This agent takes the raw text output from the `EvaluationVerificationAgent`
    and structures it according to the `EvaluationValidationOutput` schema.
    """

    def __init__(self, **kwargs: Any):
        """
        Initializes the ValidationFormattingAgent.

        Args:
            **kwargs: Keyword arguments passed to the parent `LlmAgent`.
        """
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "prompts",
            "validation_formatting_prompt.md",
        )
        with open(prompt_path, "r") as f:
            instruction = f.read()

        super().__init__(
            instruction=instruction,
            output_schema=EvaluationValidationOutput,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            generate_content_config=GENERATE_CONTENT_CONFIG,
            **kwargs,
        )


class ValidationOrchestrator(SequentialAgent):
    """
    Orchestrates the two-step validation workflow.

    This sequential agent first runs the `EvaluationVerificationAgent` to get a
    raw text analysis and then runs the `ValidationFormattingAgent` to produce
    the final, structured JSON output.
    """

    def __init__(self, **kwargs: Any):
        """
        Initializes the ValidationOrchestrator and its sub-agents.

        Args:
            **kwargs: Keyword arguments passed to the parent `SequentialAgent`.
        """
        # The verification agent uses a more powerful model for analysis.
        verification_agent = EvaluationVerificationAgent(
            name="evaluation_verification_agent",
            output_key="raw_validation_output",
            model=os.environ.get("GEMINI_PRO_MODEL", "gemini-2.5-pro"),
        )
        # The formatting agent uses a faster model for structuring the output.
        formatting_agent = ValidationFormattingAgent(
            name="validation_formatting_agent",
            output_key="validation_output",
            model=os.environ.get("GEMINI_FLASH_LITE_MODEL", "gemini-2.5-flash-lite"),
        )

        super().__init__(
            name=kwargs.get("name", "validation_orchestrator"),
            sub_agents=[
                verification_agent,
                formatting_agent,
            ],
        )
