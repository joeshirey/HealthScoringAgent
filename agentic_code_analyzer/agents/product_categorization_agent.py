from typing import AsyncGenerator
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from agentic_code_analyzer.tools.product_categorization import categorize_sample

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

        This method retrieves the code snippet, GitHub link, and region tag from
        the session state, and then uses the `categorize_sample` tool to
        categorize the code sample. It then updates the session state with the
        product category, product name, and a flag indicating whether the LLM
        was used for categorization.

        Args:
            ctx: The invocation context for the agent.

        Yields:
            An empty generator, as this agent does not produce any events.
        """
        code_snippet = ctx.session.state.get("code_snippet", "")
        github_link = ctx.session.state.get("github_link", "")
        region_tag = ctx.session.state.get("region_tag_extraction_agent_output", "")

        category, product, llm_used = categorize_sample(
            code_content=code_snippet,
            github_link=github_link,
            region_tag=region_tag,
            llm_fallback=True,
        )

        ctx.session.state["product_category"] = category
        ctx.session.state["product_name"] = product
        ctx.session.state["llm_used_for_categorization"] = llm_used

        if False:
            yield
