from google.adk.agents import LlmAgent
from google.genai import types
from google.genai.types import Tool, GoogleSearch
from agentic_code_analyzer.tools.code_cleaning import remove_comments

class InitialAnalysisAgent(LlmAgent):
    """An agent that performs the initial, detailed analysis of the code."""
    system_instructions: str = ""
    prompt_template: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open("agentic_code_analyzer/prompts/system_instructions.txt", "r") as f:
            self.system_instructions = f.read()
        with open("agentic_code_analyzer/prompts/consolidated_eval.txt", "r") as f:
            self.prompt_template = f.read()

    def _fill_prompt_placeholders(self, code_snippet, language, github_link, region_tag):
        """Fills the placeholders in the prompt template."""
        cleaned_code = remove_comments(code_snippet, language)
        prompt = self.prompt_template.replace("{{language}}", language)
        prompt = prompt.replace("{{github_link}}", github_link)
        prompt = prompt.replace("{{region_tag}}", region_tag)
        prompt = prompt.replace("{{code_sample}}", code_snippet)
        prompt = prompt.replace("{{cleaned_code}}", cleaned_code)
        return prompt

    def _get_llm_config(self):
        """Returns the configuration for the LLM."""
        return types.GenerateContentConfig(
            temperature=0.0,
            system_instruction=self.system_instructions,
            tools=[Tool(google_search=GoogleSearch())],
        )