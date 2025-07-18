import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.genai import types

load_dotenv()

MODEL = os.getenv("VERTEXAI_MODEL_NAME", "gemini-2.5-flash")

instruction_path = os.path.join(os.path.dirname(__file__), "code_eval_agent_instruction.md")
with open(instruction_path, "r") as f:
    instruction = f.read()

root_agent = Agent(
    name="code_eval_agent",
    model=MODEL,
    instruction=instruction,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.0, # More deterministic output
    ),
    description="Code validation with Google Search capabilities",
    tools=[google_search]
)
