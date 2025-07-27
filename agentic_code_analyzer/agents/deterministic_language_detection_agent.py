import logging
import re
from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of supported languages for the final output.
SUPPORTED_LANGUAGES = {
    "Python", "Java", "Go", "Ruby", "Rust", "C#", "C++", "PHP", "Terraform", "Javascript"
}

# Mapping of pygments language names to the normalized 'Javascript' name.
JAVASCRIPT_VARIANTS = {"javascript", "typescript", "node", "jsx", "tsx"}

# Keyword patterns for a first-pass, high-confidence language detection.
# These are designed to be specific to avoid clashes (e.g., Python vs. Ruby 'def').
# Using re.MULTILINE allows `^` to match the start of each line.
LANGUAGE_KEYWORDS = {
    "Python": [
        re.compile(r'^\s*def\s+\w+\(.*\):', re.MULTILINE),
        re.compile(r'^\s*class\s+\w+\(.*\):', re.MULTILINE),
        re.compile(r'^\s*import\s+(os|sys|re)\b', re.MULTILINE)
    ],
    "Java": [
        re.compile(r'import\s+java\.\w+\.'),
        re.compile(r'System\.out\.println')
    ],
    "Go": [
        re.compile(r'^\s*package\s+\w+', re.MULTILINE),
        re.compile(r'^\s*import\s+\(', re.MULTILINE),
        re.compile(r'\bfunc\b')
    ],
    "Javascript": [
        re.compile(r'\b(const|let|var)\s+\w+\s*='),
        re.compile(r'\bfunction\s*\w*\s*\(.*\)\s*\{'),
        re.compile(r'\bconsole\.log\b')
    ],
    "Ruby": [
        re.compile(r'^\s*def\s+\w+[^:]*$', re.MULTILINE),
        re.compile(r'\brequire\s+[\'"]\w+[\'"]'),
        re.compile(r'\bputs\b')
    ],
    "C#": [
        re.compile(r'^\s*using\s+System;'),
        re.compile(r'\bnamespace\s+\w+')
    ],
    "C++": [
        re.compile(r'#include\s*<[a-zA-Z0-9]+>'),
        re.compile(r'\bstd::\w+')
    ],
    "PHP": [re.compile(r'<\?php')],
    "Terraform": [re.compile(r'^\s*(resource|provider|variable|output)\s+', re.MULTILINE)],
}


class DeterministicLanguageDetectionAgent(BaseAgent):
    """
    An agent that detects language using a hybrid of keyword-based analysis
    and pygments guessing for improved accuracy.
    """

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Detects the programming language of a code snippet. It first tries a
        set of high-confidence regular expressions. If no match is found, it
        falls back to using the pygments library for a more general guess.
        """
        code_snippet = ctx.session.state.get("code_snippet", "")
        final_language = "Unknown"

        if code_snippet:
            # First, check for definitive keywords for a high-confidence match.
            for lang, patterns in LANGUAGE_KEYWORDS.items():
                if any(pattern.search(code_snippet) for pattern in patterns):
                    final_language = lang
                    logger.info(f"Language identified as '{final_language}' by keyword match.")
                    break  # Stop after the first match

            # If no keyword match, fall back to pygments for a broader analysis.
            if final_language == "Unknown":
                logger.info("No definitive keyword match found. Falling back to pygments.")
                try:
                    lexer = guess_lexer(code_snippet)
                    detected_language = lexer.name
                    logger.info(f"Pygments guessed language: {detected_language}")

                    # Normalize variants (e.g., TypeScript -> Javascript)
                    if detected_language.lower() in JAVASCRIPT_VARIANTS:
                        normalized_language = "Javascript"
                    elif detected_language == "CSharp":
                        normalized_language = "C#"
                    else:
                        normalized_language = detected_language

                    # Ensure the detected language is in our supported list.
                    if normalized_language in SUPPORTED_LANGUAGES:
                        final_language = normalized_language
                    else:
                        logger.warning(f"Pygments detected '{normalized_language}', which is not in the supported list.")

                except ClassNotFound:
                    logger.warning("Pygments could not guess the language for the snippet.")
                    # final_language remains "Unknown"

        logger.info(f"Final detected language: {final_language}")
        ctx.session.state["language_detection_agent_output"] = final_language
        ctx.session.state["LANGUAGE"] = final_language

        # This is a non-yielding generator, required by the base class.
        if False:
            yield
