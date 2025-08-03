"""
This module defines the `DeterministicLanguageDetectionAgent`, a rule-based
agent for identifying the programming language of a code snippet.
"""

import logging
import os
import re
from typing import AsyncGenerator, Dict, List, Pattern
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

# This dictionary contains regular expressions for content-based language
# detection. It serves as a fallback when file extension analysis is not
# possible. The order of languages is important to avoid misclassification,
# with more specific languages appearing before more general ones.
LANGUAGE_KEYWORDS: Dict[str, List[Pattern[str]]] = {
    # PHP's opening tag is highly distinctive.
    "PHP": [
        re.compile(r"<\?php"),
        re.compile(r"\bpublic\s+function\s+"),
        re.compile(r"->\w+"),
    ],
    # C#'s `using System;` and namespace syntax are strong indicators.
    "C#": [
        re.compile(r"^\s*using\s+System(\.\w*)*;", re.MULTILINE),
        re.compile(r"\bnamespace\s+[\w\.]+"),
        re.compile(r"\{\s*get;\s*(private\s*)?set;\s*\}"),
    ],
    # Java's `import java.` and main method signature are very specific.
    "Java": [
        re.compile(r"^\s*import\s+java\.\w+\.\w+;", re.MULTILINE),
        re.compile(r"public\s+static\s+void\s+main\s*\(String"),
    ],
    # Python's `def` and `import` syntax are common and reliable.
    "Python": [
        re.compile(r"^\s*def\s+\w+\(.*\):", re.MULTILINE),
        re.compile(r"^\s*import\s+(os|sys|re)\b", re.MULTILINE),
    ],
    # Go's `package` and `func` keywords are strong signals.
    "Go": [
        re.compile(r"^\s*package\s+\w+", re.MULTILINE),
        re.compile(r"^\s*import\s+\(", re.MULTILINE),
        re.compile(r"\bfunc\s+\w+\s*\(.*\)\s*\{"),
    ],
    # Ruby's `def` syntax is distinct from Python's (no colon).
    "Ruby": [
        re.compile(r"^\s*def\s+\w+[^:]*$", re.MULTILINE),
        re.compile(r'\brequire\s+[\'"]\w+[\'"]'),
    ],
    # C++ is often identified by its `#include` directives.
    "C++": [
        re.compile(r"^\s*#include\s*<[a-zA-Z0-9]+>", re.MULTILINE),
        re.compile(r"\bstd::(cout|vector|string)"),
    ],
    # Rust has several unique keywords like `fn`, `let mut`, and `use`.
    "Rust": [
        re.compile(r"\b(fn|struct|enum|impl|let\s+mut|use\s+std::)\s+"),
        re.compile(r"println!\s*\("),
    ],
    # Terraform's declarative syntax is easy to spot.
    "Terraform": [
        re.compile(r"^\s*(resource|provider|variable|output)\s+", re.MULTILINE)
    ],
    # Javascript is placed last because its keywords can be ambiguous.
    "Javascript": [
        re.compile(r"\b(const|let|var)\s+\w+\s*="),
        re.compile(r"\bconsole\.log\s*\("),
    ],
}


class DeterministicLanguageDetectionAgent(BaseAgent):
    """
    Detects programming language using a deterministic, two-step approach.

    This agent first attempts to identify the language from the file extension
    of a `github_link` provided in the session state. If this is not possible,
    it falls back to a keyword-based regular expression analysis of the
    `code_snippet`. This hybrid approach is fast, reliable, and does not
    require an LLM.
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
        code_snippet = ctx.session.state.get("code_snippet", "")
        final_language = ""

        # Step 1: Attempt to detect the language from the file extension.
        # This is the most reliable method.
        if github_link:
            try:
                parsed_url = urlparse(github_link)
                _, extension = os.path.splitext(parsed_url.path)
                if extension in FILE_EXTENSION_MAP:
                    final_language = FILE_EXTENSION_MAP[extension]
                    logger.info(
                        f"Language identified as '{final_language}' from "
                        f"file extension '{extension}'."
                    )
            except Exception as e:
                logger.warning(
                    f"Could not parse GitHub link '{github_link}': {e}",
                    exc_info=True,
                )

        # Step 2: If file extension detection fails, fall back to content analysis.
        if not final_language:
            if code_snippet:
                final_language = "Unknown"
                logger.info("Falling back to content-based language detection.")
                for lang, patterns in LANGUAGE_KEYWORDS.items():
                    if any(pattern.search(code_snippet) for pattern in patterns):
                        final_language = lang
                        logger.info(
                            f"Language identified as '{lang}' by keyword match."
                        )
                        break  # Stop after the first successful match.
            else:
                final_language = "Unknown"

        if final_language == "Unknown":
            logger.warning(
                "Could not determine language from file extension or keywords."
            )

        # Update the session state with the detected language.
        logger.info(f"Final detected language: {final_language}")
        ctx.session.state["language_detection_agent_output"] = final_language
        ctx.session.state["LANGUAGE"] = final_language

        # This is a non-yielding generator, required by the base class.
        if False:
            yield
