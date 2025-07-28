"""
This module defines the `ProductCategorizationAgent`, which is responsible for
identifying the product and product category associated with a code sample.
"""

import logging
from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from agentic_code_analyzer.tools.product_categorization import categorize_sample

logger = logging.getLogger(__name__)


class ProductCategorizationAgent(BaseAgent):
    """
    Categorizes a code sample into a product and product category.

    This agent acts as a wrapper around the `categorize_sample` tool, which
    uses a combination of rules-based logic and an optional LLM fallback to
    determine the product context of the code.
    """

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Categorizes the code sample and updates the session state.

        Args:
            ctx: The invocation context for the current agent run, containing
                the session state with `code_snippet`, `github_link`, and
                `region_tag_extraction_agent_output`.

        Yields:
            This is a non-yielding generator, required by the base class.
        """
        logger.info(f"[{self.name}] Starting product categorization.")
        code_snippet = ctx.session.state.get("code_snippet", "")
        github_link = ctx.session.state.get("github_link", "")
        region_tag = ctx.session.state.get("region_tag_extraction_agent_output", "")

        # The categorize_sample function contains the core logic for this step.
        category, product, llm_used = categorize_sample(
            code_content=code_snippet,
            github_link=github_link,
            region_tag=region_tag,
            llm_fallback=True,  # Enable LLM for ambiguous cases.
        )

        logger.info(
            f"[{self.name}] Categorized as '{product}' in '{category}'. "
            f"LLM used: {llm_used}."
        )

        # Store the results in the session state for downstream agents.
        ctx.session.state["product_category"] = category
        ctx.session.state["product_name"] = product
        ctx.session.state["llm_used_for_categorization"] = llm_used

        # This is a non-yielding generator, required by the base class.
        if False:
            yield
