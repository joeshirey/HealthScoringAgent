"""
This module defines the `DeterministicLanguageDetectionAgent`, a rule-based
agent for identifying the programming language of a code snippet.
"""

import logging
import os
from typing import AsyncGenerator, Dict
from urllib.parse import urlparse

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This mapping provides a fast and reliable way to identify the language
# from a file extension. It is the preferred method of detection.
FILE_EXTENSION_MAP: Dict[str, str] = {
    ".py": "Python",
    ".java": "Java",
    ".groovy": "Java",
    ".kt": "Java",
    ".scala": "Java",
    ".go": "Go",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".cs": "C#",
    ".cpp": "C++",
    ".cc": "C++",
    ".h": "C++",
    ".c": "C++",
    ".hpp": "C++",
    ".php": "PHP",
    ".tf": "Terraform",
    ".js": "JavaScript",
    ".ts": "JavaScript",  # TypeScript is normalized to Javascript.
    ".jsx": "JavaScript",
    ".tsx": "JavaScript",
    ".sh": "Unknown",
    ".yaml": "Unknown",
    ".xml": "Unknown",
}



class DeterministicLanguageDetectionAgent(BaseAgent):
    """
    Detects programming language using a deterministic approach based on file
    extensions.

    This agent identifies the language from the file extension of a
    `github_link` provided in the session state. If the extension is not
    recognized, it defaults to "Unknown". This approach is fast, reliable, and
    does not require an LLM.
    """

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Detects the programming language and updates the session state.

        Args:
            ctx: The invocation context for the current agent run, containing
                the session state with `github_link` and `code_snippet`.

        Yields:
            This is a non-yielding generator, required by the base class.
        """
        github_link = ctx.session.state.get("github_link")
        final_language = "Unknown"

        if github_link:
            try:
                parsed_url = urlparse(github_link)
                _, extension = os.path.splitext(parsed_url.path)
                language = FILE_EXTENSION_MAP.get(extension)
                if language:
                    final_language = language
                    logger.info(
                        f"Language identified as '{final_language}' from "
                        f"file extension '{extension}'."
                    )
                else:
                    logger.warning(
                        f"Unknown file extension '{extension}'. "
                        "Defaulting to 'Unknown'."
                    )
            except Exception as e:
                logger.warning(
                    f"Could not parse GitHub link '{github_link}': {e}",
                    exc_info=True,
                )
        else:
            logger.warning("No GitHub link provided. Cannot determine language.")

        if final_language == "Unknown":
            logger.warning("Could not determine language from file extension.")

        # Update the session state with the detected language.
        logger.info(f"Final detected language: {final_language}")
        ctx.session.state["language_detection_agent_output"] = final_language
        ctx.session.state["LANGUAGE"] = final_language

        # This is a non-yielding generator, required by the base class.
        if False:
            yield
