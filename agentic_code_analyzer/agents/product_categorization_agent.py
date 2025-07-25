from typing import AsyncGenerator
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from agentic_code_analyzer.tools.product_categorization import categorize_sample

class ProductCategorizationAgent(BaseAgent):
    """An agent that categorizes the code sample into a product."""

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        code_snippet = ctx.session.state.get("code_snippet", "")
        github_link = ctx.session.state.get("github_link")
        region_tag = ctx.session.state.get("region_tag_extraction_agent_output")

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