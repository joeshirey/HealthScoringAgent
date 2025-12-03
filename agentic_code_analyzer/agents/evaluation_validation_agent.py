"""
This module defines the agents responsible for the validation workflow.

This includes the `ValidationOrchestrator` and its sub-agents, which are
designed to verify the accuracy of an initial code analysis.
"""

import json
import os
from typing import Any

from google.adk.agents import LlmAgent
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


