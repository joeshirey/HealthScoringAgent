"""
This module defines the `ProductIdentificationAgent`, a simple LLM-based agent
for identifying the Google Cloud product associated with a code snippet.

Note: This agent is a simpler, less-robust alternative to the hybrid
`ProductCategorizationAgent`. It is retained as an example of a basic
LLM-only agent but is not used in the main orchestration workflow.
"""

from google.adk.agents import LlmAgent


class ProductIdentificationAgent(LlmAgent):
    """
    An agent that identifies the product and category from a code snippet.

    This agent uses a fixed prompt to instruct a large language model (LLM) to
    analyze a code snippet and determine the relevant Google Cloud product and
    product category.
    """

    def __init__(self, **kwargs):
        """Initializes the ProductIdentificationAgent."""
        # Load the instruction prompt from an external markdown file.
        with open("agentic_code_analyzer/prompts/product_identification.md", "r") as f:
            instruction = f.read()
        super().__init__(instruction=instruction, **kwargs)
