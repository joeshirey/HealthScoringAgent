"""
This module defines the `DeterministicRegionTagAgent`, a non-LLM agent that
efficiently extracts region tags from a code snippet.

Region tags (e.g., `[START vision_face_detection]`) are a common convention in
code samples for identifying specific, meaningful blocks of code. This agent
uses a simple and fast regular expression to find all unique `[START ...]` and
`[END ...]` tags. This deterministic approach avoids LLM costs and provides
reliable metadata for the initial phase of the analysis workflow.
"""

import logging
import re
from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

logger = logging.getLogger(__name__)


class DeterministicRegionTagAgent(BaseAgent):
    """
    Extracts region tags from a code snippet using regular expressions.

    This agent uses a deterministic, non-LLM approach to find all unique
    `[START ...]` and `[END ...]` tags within the provided code and stores
    them as a comma-separated string in the session state.
    """

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Extracts unique region tags and updates the session state.

        Args:
            ctx: The invocation context for the current agent run, containing
                the session state with the `code_snippet`.

        Yields:
            This is a non-yielding generator, required by the base class.
        """
        logger.info(f"[{self.name}] Starting region tag extraction.")
        code_snippet = ctx.session.state.get("code_snippet", "")

        # Regular expression to find all [START ...] and [END ...] tags.
        # It captures the alphanumeric identifier within the tag.
        start_tags = re.findall(r"\[START\s+([a-zA-Z0-9_]+)\]", code_snippet)
        end_tags = re.findall(r"\[END\s+([a-zA-Z0-9_]+)\]", code_snippet)

        # Combine the lists of start and end tags, then use a set to find
        # unique tags, and finally sort them for consistent output.
        all_tags = sorted(list(set(start_tags + end_tags)))

        tags_str = ",".join(all_tags)
        logger.info(f"[{self.name}] Found {len(all_tags)} unique region tags.")

        # Store the result in the session state for other agents to use.
        ctx.session.state["region_tag_extraction_agent_output"] = tags_str

        # This is a non-yielding generator, required by the base class.
        if False:
            yield
