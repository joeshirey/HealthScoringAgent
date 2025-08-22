"""
This module defines the ValidationAgent for the Health Scoring Agent.

The `ValidationAgent` acts as a critical gatekeeper in the analysis workflow.
It performs essential pre-checks on the output of the initial detection phase
(language and region tags). If these checks fail, it halts the entire
orchestration to prevent wasted processing on invalid or unsupported inputs.
This fail-fast approach improves the efficiency and reliability of the system.
"""

import json
import logging
from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai.types import Content, Part

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {
    "C#",
    "C++",
    "Go",
    "Java",
    "JavaScript",
    "PHP",
    "Python",
    "Ruby",
    "Terraform",
    "TypeScript",
}


class ValidationAgent(BaseAgent):
    """
    An agent that validates the output of the initial detection phase.

    This agent checks for two conditions:
    1.  If region tags were extracted.
    2.  If the detected language is one of the supported languages.

    If either of these conditions is not met, the agent will yield a final
    error message and stop the workflow by setting `turn_complete=True`.
    """

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Runs the validation logic.

        Args:
            ctx: The invocation context for the current agent run.

        Yields:
            An Event with `turn_complete=True` if validation fails, halting
            the parent `SequentialAgent`.
        """
        logger.info(f"[{self.name}] Running validation checks.")

        region_tags = ctx.session.state.get("region_tag_extraction_agent_output", "")
        language = ctx.session.state.get("language_detection_agent_output", "Unknown")

        if not region_tags:
            logger.warning(f"[{self.name}] Validation failed: No region tags found.")
            error_response = json.dumps({"error": "No Region Tags"})
            yield Event(
                author=self.name,
                content=Content(parts=[Part(text=error_response)]),
                turn_complete=True,
            )
            return  # Stop further execution of this agent

        if language not in SUPPORTED_LANGUAGES:
            logger.warning(
                f"[{self.name}] Validation failed: Unsupported language '{language}'."
            )
            error_response = json.dumps({"error": "Unsupported Language"})
            yield Event(
                author=self.name,
                content=Content(parts=[Part(text=error_response)]),
                turn_complete=True,
            )
            return  # Stop further execution of this agent

        logger.info(f"[{self.name}] Validation checks passed.")
        # If validation passes, yield nothing and allow the orchestrator to continue.
