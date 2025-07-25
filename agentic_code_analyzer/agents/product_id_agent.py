from google.adk.agents import LlmAgent

class ProductIdentificationAgent(LlmAgent):
    """An agent that identifies the product and category from a code snippet."""

    def __init__(self, **kwargs):
        super().__init__(
            instruction="You are an expert at identifying Google Cloud products from code snippets. Your task is to analyze the provided code and determine the specific Google Cloud product and its primary category. For example, if the code uses `google.cloud.vision`, the product is \"Vision AI\" and the category is \"AI / Machine Learning\". Respond with the product name and category, separated by a comma. For example: `Vision AI,AI / Machine Learning`. If you cannot determine the product, respond with `Unknown,Unknown`. The code snippet is: {code_snippet}",
            **kwargs
        )
