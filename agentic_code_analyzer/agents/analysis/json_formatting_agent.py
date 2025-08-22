"""
This module defines the `JsonFormattingAgent`, a specialized utility agent that
converts the unstructured text output from the `InitialAnalysisAgent` into a
clean, structured JSON object.

By dedicating a separate agent to formatting, the system can use a faster, more
cost-effective LLM for this simpler task, while reserving the more powerful
model for the complex analytical work. This design pattern improves the overall
efficiency and reliability of the analysis pipeline, ensuring that the final
output is always programmatically accessible.
"""

from typing import Any

from google.adk.agents import LlmAgent


class JsonFormattingAgent(LlmAgent):
    """
    Formats raw text analysis into a structured JSON object.

    This agent takes the unstructured text output from the `InitialAnalysisAgent`
    and uses a fast, lightweight large language model (LLM) to convert it into
    a clean, structured JSON object that conforms to a predefined schema. This
    separation of concerns (analysis vs. formatting) improves reliability and
    allows for the use of different models for each task.
    """

    def __init__(self, **kwargs: Any):
        """
        Initializes the JsonFormattingAgent.

        This method loads the JSON conversion prompt and initializes the
        `LlmAgent`.

        Args:
            **kwargs: Keyword arguments passed to the parent `LlmAgent`.
        """
        # Load the prompt that instructs the LLM on how to format the JSON.
        with open("agentic_code_analyzer/prompts/json_conversion.md", "r") as f:
            prompt_template = f.read()

        # Initialize the LlmAgent with the formatting instruction.
        super().__init__(instruction=prompt_template, **kwargs)
