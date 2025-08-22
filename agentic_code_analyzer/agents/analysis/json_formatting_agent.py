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

from google.adk.agents import LlmAgent


class JsonFormattingAgent(LlmAgent):
    """
    Formats raw text analysis into a structured JSON object.

    This agent takes the unstructured text output from the `InitialAnalysisAgent`
    and uses a fast, lightweight large language model (LLM) to convert it into
    a structured `AnalysisResult` object. It leverages the `output_schema`
    feature of the ADK to ensure the output is always a valid, typed object,
    improving the reliability of the analysis pipeline.
    """
