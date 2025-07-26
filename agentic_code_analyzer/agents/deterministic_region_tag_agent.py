import re
from typing import AsyncGenerator
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai.types import Content, Part

class DeterministicRegionTagAgent(BaseAgent):
    """
    An agent that extracts region tags from a code snippet using a deterministic
    regular expression-based approach.
    """

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Extracts all unique region tags from the code snippet in the session state.
        """
        code_snippet = ctx.session.state.get("code_snippet", "")
        
        # Regex to find all [START ...] and [END ...] tags
        start_tags = re.findall(r"\[START\s+([a-zA-Z0-9_]+)\]", code_snippet)
        end_tags = re.findall(r"\[END\s+([a-zA-Z0-9_]+)\]", code_snippet)
        
        # Combine and find unique tags
        all_tags = sorted(list(set(start_tags + end_tags)))
        
        tags_str = ",".join(all_tags)
        
        ctx.session.state["region_tag_extraction_agent_output"] = tags_str
        
        # This is a non-yielding generator
        if False:
            yield
