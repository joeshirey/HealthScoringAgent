import logging
from typing import AsyncGenerator
import re
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

logger = logging.getLogger(__name__)


class CodeCleaningAgent(BaseAgent):
    """
    An agent that removes comments from a code snippet based on its language.
    """

    def _remove_comments(self, code: str, language: str) -> str:
        """
        Removes comments from a code string based on the language.
        """
        if language.lower() in ["python", "shell", "ruby"]:
            return re.sub(r"#.*", "", code)
        elif language.lower() in [
            "javascript",
            "java",
            "c",
            "c++",
            "c#",
            "go",
            "swift",
            "typescript",
            "kotlin",
            "rust",
            "php",
            "terraform",
        ]:
            code = re.sub(r"//.*", "", code)
            code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
            return code
        elif language.lower() in ["html", "xml"]:
            return re.sub(r"<!--.*?-->", "", code, flags=re.DOTALL)
        else:
            return code

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Retrieves code and language from state, cleans the code, and saves it back.
        """
        logger.info(f"[{self.name}] Starting code cleaning.")
        code_snippet = ctx.session.state.get("code_snippet", "")
        language = ctx.session.state.get("language_detection_agent_output", "Unknown")

        cleaned_code = self._remove_comments(code_snippet, language)
        logger.info(f"[{self.name}] Code cleaning complete for language: {language}.")

        ctx.session.state["cleaned_code"] = cleaned_code

        if False:
            yield
