import asyncio
import json
from fastapi import FastAPI
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agentic_code_analyzer.orchestrator import CodeAnalyzerOrchestrator

app = FastAPI()

class CodeRequest(BaseModel):
    code: str
    github_link: str = None

@app.post("/analyze")
async def analyze_code(request: CodeRequest):
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="agentic_code_analyzer",
        user_id="api_user",
        session_id="api_session",
        state={"code_snippet": request.code, "github_link": request.github_link},
    )

    runner = Runner(
        agent=CodeAnalyzerOrchestrator(name="code_analyzer_orchestrator"),
        app_name="agentic_code_analyzer",
        session_service=session_service,
    )

    final_response = ""
    async for event in runner.run_async(
        user_id="api_user",
        session_id="api_session",
        new_message=types.Content(parts=[types.Part(text=request.code)]),
    ):
        if event.is_final_response():
            final_response = event.content.parts[0].text

    return json.loads(final_response)