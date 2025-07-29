"""
This module defines the validation agent for the Health Scoring Agent.
"""

import json
import logging
from typing import AsyncGenerator, List

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai.types import Content, Part

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


class ValidationAgent(BaseAgent):
    """
    An agent that validates the output of the initial detection phase.
    """

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Executes the validation logic.
        """
        logger.info(f"[{self.name}] Starting validation.")

        region_tags = ctx.session.state.get("region_tag_extraction_agent_output")
        if not region_tags:
            logger.error(f"[{self.name}] No region tags found.")
            yield Event(
                author=self.name,
                content=Content(parts=[Part(text=json.dumps({"error": "No Region Tags"}))]),
                turn_complete=True,
            )
            return

        language = ctx.session.state.get("language_detection_agent_output")
        if language not in SUPPORTED_LANGUAGES:
            logger.error(f"[{self.name}] Unsupported language: {language}")
            yield Event(
                author=self.name,
                content=Content(
                    parts=[Part(text=json.dumps({"error": "Unsupported language"}))]
                ),
                turn_complete=True,
            )
            return
        logger.info(f"[{self.name}] Validation successful.")
