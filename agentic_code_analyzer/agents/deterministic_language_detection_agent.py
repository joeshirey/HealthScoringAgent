import logging
import re
import os
from urllib.parse import urlparse
from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# A mapping from file extensions to the official language name.
# This is the primary, most reliable method of language detection.
FILE_EXTENSION_MAP = {
    ".py": "Python",
    ".java": "Java",
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
    ".js": "Javascript",
    ".ts": "Javascript",  # Normalizing TypeScript to Javascript
    ".jsx": "Javascript",
    ".tsx": "Javascript",
}

# A dictionary of regular expressions for content-based analysis.
# This serves as a fallback if file extension detection fails.
# The order is important to prevent misclassification.
LANGUAGE_KEYWORDS = {
    # PHP has a very distinctive opening tag.
    "PHP": [
        re.compile(r"<\?php"),
        re.compile(r"\bpublic\s+function\s+"),
        re.compile(r"->\w+"),
    ],
    # C# is specific with `using` and properties.
    "C#": [
        re.compile(r"^\s*using\s+System(\.\w*)*;", re.MULTILINE),
        re.compile(r"\bnamespace\s+[\w\.]+"),
        re.compile(r"\{\s*get;\s*(private\s*)?set;\s*\}"),
    ],
    # Java is specific with its `import java.` and main method signature.
    "Java": [
        re.compile(r"^\s*import\s+java\.\w+\.\w+;", re.MULTILINE),
        re.compile(r"public\s+static\s+void\s+main\s*\(String"),
    ],
    # Python's syntax is quite regular.
    "Python": [
        re.compile(r"^\s*def\s+\w+\(.*\):", re.MULTILINE),
        re.compile(r"^\s*import\s+(os|sys|re)\b", re.MULTILINE),
    ],
    # Go's package and func syntax are strong indicators.
    "Go": [
        re.compile(r"^\s*package\s+\w+", re.MULTILINE),
        re.compile(r"^\s*import\s+\(", re.MULTILINE),
        re.compile(r"\bfunc\s+\w+\s*\(.*\)\s*\{"),
    ],
    # Ruby's `def` syntax is distinct from Python's.
    "Ruby": [
        re.compile(r"^\s*def\s+\w+[^:]*$", re.MULTILINE),
        re.compile(r'\brequire\s+[\'"]\w+[\'"]'),
    ],
    # C++ relies on `#include`.
    "C++": [
        re.compile(r"^\s*#include\s*<[a-zA-Z0-9]+>", re.MULTILINE),
        re.compile(r"\bstd::(cout|vector|string)"),
    ],
    # Rust has several unique keywords.
    "Rust": [
        re.compile(r"\b(fn|struct|enum|impl|let\s+mut|use\s+std::)\s+"),
        re.compile(r"println!\s*\("),
    ],
    # Terraform's syntax is very declarative.
    "Terraform": [
        re.compile(r"^\s*(resource|provider|variable|output)\s+", re.MULTILINE)
    ],
    # Javascript is last as its keywords are more common.
    "Javascript": [
        re.compile(r"\b(const|let|var)\s+\w+\s*="),
        re.compile(r"\bconsole\.log\s*\("),
    ],
}


class DeterministicLanguageDetectionAgent(BaseAgent):
    """
    An agent that detects language using a hybrid approach:
    1. It first attempts to determine the language from the file extension of a
       `github_link` in the session state.
    2. If that fails, it falls back to a keyword-based regex analysis of the
       `code_snippet`.
    """

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Detects the programming language using the hybrid strategy.
        """
        github_link = ctx.session.state.get("github_link")
        code_snippet = ctx.session.state.get("code_snippet", "")
        final_language = "Unknown"

        # 1. Try to detect language from the file extension.
        if github_link:
            try:
                parsed_url = urlparse(github_link)
                _, extension = os.path.splitext(parsed_url.path)
                if extension in FILE_EXTENSION_MAP:
                    final_language = FILE_EXTENSION_MAP[extension]
                    logger.info(
                        f"Language identified as '{final_language}' from file extension '{extension}'."
                    )
            except Exception as e:
                logger.warning(f"Could not parse GitHub link '{github_link}': {e}")

        # 2. If extension detection fails, fall back to content analysis.
        if final_language == "Unknown" and code_snippet:
            logger.info("Falling back to content-based language detection.")
            for lang, patterns in LANGUAGE_KEYWORDS.items():
                if any(pattern.search(code_snippet) for pattern in patterns):
                    final_language = lang
                    logger.info(f"Language identified as '{lang}' by keyword match.")
                    break  # Stop after the first match

        if final_language == "Unknown":
            logger.warning(
                "Could not determine language from file extension or keywords."
            )

        logger.info(f"Final detected language: {final_language}")
        ctx.session.state["language_detection_agent_output"] = final_language
        ctx.session.state["LANGUAGE"] = final_language

        # This is a non-yielding generator, required by the base class.
        if False:
            yield
