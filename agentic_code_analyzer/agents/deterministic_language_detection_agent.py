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

SUPPORTED_LANGUAGES = {
    "Python", "Java", "Go", "Ruby", "Rust", "C#", "C++", "PHP", "Terraform", "Javascript"
}
JAVASCRIPT_VARIANTS = {"javascript", "typescript", "node", "jsx", "tsx"}

# Keyword patterns for tie-breaking or forcing a language choice.
LANGUAGE_KEYWORDS = {
    "Java": [re.compile(r'\b(public|private|protected)\s+(class|interface|enum)')],
    "Python": [re.compile(r'\b(def|class)\s+\w+\s*:')],
    "Go": [re.compile(r'\b(package|import|func)\s+')],
    "Javascript": [re.compile(r'\b(const|let|var|function|import|export)\s+')],
    "Ruby": [re.compile(r'\b(def|class|module)\s+')],
    "Rust": [re.compile(r'\b(fn|struct|enum|impl)\s+')],
    "C#": [re.compile(r'\b(public|private|protected)\s+(class|interface|enum)')],
    "C++": [re.compile(r'\b(class|struct|enum|namespace)\s+')],
    "PHP": [re.compile(r'<\?php')],
    "Terraform": [re.compile(r'\b(resource|provider|variable|output)\s+')],
}

class DeterministicLanguageDetectionAgent(BaseAgent):
    """
    An agent that detects language using a hybrid of pygments guessing and
    keyword-based analysis for improved accuracy.
    """

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        code_snippet = ctx.session.state.get("code_snippet", "")
        final_language = "Unknown"

        if code_snippet:
            # First, check for definitive keywords.
            for lang, patterns in LANGUAGE_KEYWORDS.items():
                if any(pattern.search(code_snippet) for pattern in patterns):
                    final_language = lang
                    logger.info(f"Language forced to '{final_language}' by keyword match.")
                    break
            
            # If no keyword match, fall back to pygments.
            if final_language == "Unknown":
                try:
                    lexer = guess_lexer(code_snippet)
                    detected_language = lexer.name
                    logger.info(f"Pygments guessed language: {detected_language}")

                    if detected_language.lower() in JAVASCRIPT_VARIANTS:
                        normalized_language = "Javascript"
                    elif detected_language == "CSharp":
                        normalized_language = "C#"
                    else:
                        normalized_language = detected_language

                    if normalized_language in SUPPORTED_LANGUAGES:
                        final_language = normalized_language
                except ClassNotFound:
                    logger.warning("Pygments could not guess the language.")
                    final_language = "Unknown"

        logger.info(f"Final detected language: {final_language}")
        ctx.session.state["language_detection_agent_output"] = final_language
        ctx.session.state["LANGUAGE"] = final_language
        
        if False:
            yield
