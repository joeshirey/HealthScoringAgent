from google.adk.agents import LlmAgent


class ProductIdentificationAgent(LlmAgent):
    """An agent that identifies the product and category from a code snippet."""

    def __init__(self, **kwargs):
        with open("agentic_code_analyzer/prompts/product_identification.md", "r") as f:
            instruction = f.read()
        super().__init__(instruction=instruction, **kwargs)
