"""
This module defines the `InitialAnalysisAgent`, the primary analytical agent in
the Health Scoring system.

This agent is responsible for conducting the deep, qualitative review of the
code. It is designed to act as a "Principal Software Engineer," leveraging a
powerful LLM and the Google Search tool to perform a comprehensive, multi-faceted
evaluation. Its output is a detailed, unstructured text review, which is then
passed to a separate agent for formatting. This separation of concerns allows
this agent to focus purely on the quality of the analysis.
"""

from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import google_search


class InitialAnalysisAgent(LlmAgent):
    """
    Performs the initial, detailed, tool-based analysis of the code.

    This agent uses a powerful large language model (LLM) and the Google Search
    tool to conduct a comprehensive review of the code. It is guided by a
    detailed set of system instructions and a prompt template that directs it
    to evaluate multiple criteria, such as code quality, runnability, and API
    effectiveness. The output of this agent is a raw text analysis that is then
    passed to a formatting agent.
    """

    def __init__(self, **kwargs: Any):
        """
        Initializes the InitialAnalysisAgent.

        This method loads the system instructions and the main evaluation prompt
        from markdown files, combines them, and initializes the `LlmAgent` with
        the resulting instruction and the `google_search` tool.

        Args:
            **kwargs: Keyword arguments passed to the parent `LlmAgent`.
        """
        # Load the system instructions that define the agent's persona and goals.
        with open("agentic_code_analyzer/prompts/system_instructions.md", "r") as f:
            system_instructions = f.read()

        # Load the prompt template for the main evaluation task.
        with open("agentic_code_analyzer/prompts/consolidated_eval.md", "r") as f:
            prompt_template = f.read()

        # Combine the instructions and template to form the full prompt.
        instruction = f"{system_instructions}\n\n{prompt_template}"

        # Initialize the LlmAgent with the combined instruction and tools.
        super().__init__(instruction=instruction, tools=[google_search], **kwargs)
