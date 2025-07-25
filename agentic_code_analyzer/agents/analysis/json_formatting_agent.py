from google.adk.agents import LlmAgent
from google.genai import types

class JsonFormattingAgent(LlmAgent):
    """An agent that formats the raw text analysis into a JSON object."""
    prompt_template: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open("agentic_code_analyzer/prompts/json_conversion.txt", "r") as f:
            self.prompt_template = f.read()

    def _fill_prompt_placeholders(self, text_to_format):
        """Fills the placeholders in the prompt template."""
        return self.prompt_template.replace("{{text}}", text_to_format)

    def _get_llm_config(self):
        """Returns the configuration for the LLM."""
        return types.GenerateContentConfig(
            temperature=0.0,
            top_p=0.9,
            seed=5,
        )