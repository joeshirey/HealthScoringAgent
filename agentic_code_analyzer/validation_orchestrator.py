"""
This module defines the validation orchestrator for the Health Scoring Agent.

It coordinates the validation workflow, which uses specialized agents to
verify the accuracy of an initial code analysis.
"""

import os
from typing import Any

from google.adk.agents import SequentialAgent

from agentic_code_analyzer.agents.evaluation_validation_agent import (
    EvaluationVerificationAgent,
    ValidationFormattingAgent,
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