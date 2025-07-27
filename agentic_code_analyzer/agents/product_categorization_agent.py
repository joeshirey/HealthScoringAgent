import logging
from typing import AsyncGenerator
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from agentic_code_analyzer.tools.product_categorization import categorize_sample

logger = logging.getLogger(__name__)

class ProductCategorizationAgent(BaseAgent):
    """
    An agent that categorizes the code sample into a product.

    This agent uses a combination of rules-based logic and a large language
    model to categorize the code sample into a specific product and product
    category. It is designed to be accurate and reliable, even in ambiguous
    cases.
    """

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Categorizes the code sample and updates the session state with the
        results.
        """
        logger.info(f"[{self.name}] Starting product categorization.")
        code_snippet = ctx.session.state.get("code_snippet", "")
        github_link = ctx.session.state.get("github_link", "")
        region_tag = ctx.session.state.get("region_tag_extraction_agent_output", "")

        category, product, llm_used = categorize_sample(
            code_content=code_snippet,
            github_link=github_link,
            region_tag=region_tag,
            llm_fallback=True,
        )
        
        logger.info(f"[{self.name}] Categorized as '{product}' in '{category}'. LLM used: {llm_used}.")

        ctx.session.state["product_category"] = category
        ctx.session.state["product_name"] = product
        ctx.session.state["llm_used_for_categorization"] = llm_used

        if False:
            yield
