"""
This module defines the `CodeCleaningAgent`, which is responsible for removing
comments from a code snippet before it is analyzed.
"""
import logging
import re
from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

logger = logging.getLogger(__name__)


class CodeCleaningAgent(BaseAgent):
    """
    Removes comments from a code snippet based on its detected language.

    This agent ensures that the subsequent analysis is performed only on the
    executable code, preventing comments from influencing the evaluation.
    """

    def _remove_comments(self, code: str, language: str) -> str:
        """
        Removes comments from a code string using language-specific regex.

        Args:
            code: The source code to clean.
            language: The programming language of the code.

        Returns:
            The code with comments removed.
        """
        lang_lower = language.lower()

        # Handles languages with hash-based single-line comments (e.g., Python, Ruby).
        if lang_lower in ["python", "shell", "ruby"]:
            return re.sub(r"#.*", "", code)

        # Handles languages with C-style comments (e.g., JS, Java, C++, Go).
        elif lang_lower in [
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
            # Remove single-line comments (//...).
            code = re.sub(r"//.*", "", code)
            # Remove multi-line comments (/*...*/). The DOTALL flag allows `.`
            # to match newlines, and `*?` makes the match non-greedy.
            code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
            return code

        # Handles languages with HTML-style comments.
        elif lang_lower in ["html", "xml"]:
            return re.sub(r"<!--.*?-->", "", code, flags=re.DOTALL)

        # If the language is not supported, return the original code.
        else:
            logger.warning(
                f"[{self.name}] Comment removal not supported for language "
                f"'{language}'. Returning original code."
            )
            return code

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Retrieves code and language from state, cleans it, and saves it back.

        Args:
            ctx: The invocation context for the current agent run.

        Yields:
            This is a non-yielding generator, required by the base class.
        """
        logger.info(f"[{self.name}] Starting code cleaning.")
        code_snippet = ctx.session.state.get("code_snippet", "")
        language = ctx.session.state.get("language_detection_agent_output", "Unknown")

        cleaned_code = self._remove_comments(code_snippet, language)
        logger.info(
            f"[{self.name}] Code cleaning complete for language: {language}."
        )

        # Store the cleaned code in the session state.
        ctx.session.state["cleaned_code"] = cleaned_code

        # This is a non-yielding generator, required by the base class.
        if False:
            yield
