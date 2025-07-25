import asyncio
import asyncio
import json
import re
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agentic_code_analyzer.orchestrator import CodeAnalyzerOrchestrator

app = FastAPI()

def remove_comments(code: str, language: str) -> str:
    """
    Removes comments from a code string based on the language.
    """
    if language.lower() in ["python", "shell", "ruby"]:
        # Removes single-line comments starting with #
        return re.sub(r"#.*", "", code)
    elif language.lower() in ["javascript", "java", "c", "c++", "c#", "go", "swift", "typescript", "kotlin", "rust", "php"]:
        # Removes single-line // comments and multi-line /* ... */ comments
        code = re.sub(r"//.*", "", code)
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
        return code
    elif language.lower() in ["html", "xml"]:
        # Removes <!-- ... --> comments
        return re.sub(r"<!--.*?-->", "", code, flags=re.DOTALL)
    else:
        # Return original code if language is not supported
        return code

class CodeRequest(BaseModel):
    code: str
    github_link: str = None

class GitHubLinkRequest(BaseModel):
    github_link: str

@app.post("/analyze")
async def analyze_code(request: CodeRequest):
    session_service = InMemorySessionService()
    # This is a temporary solution to determine the language.
    # In a real application, you would use a more robust method.
    language = "python" # Assuming python for now
    cleaned_code = remove_comments(request.code, language)
    session = await session_service.create_session(
        app_name="agentic_code_analyzer",
        user_id="api_user",
        session_id="api_session",
        state={
            "code_snippet": request.code,
            "github_link": request.github_link,
            "cleaned_code": cleaned_code,
            "language": language,
            "LANGUAGE": language,
        },
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

@app.post("/analyze_github_link")
async def analyze_github_link(request: GitHubLinkRequest):
    try:
        raw_url = request.github_link.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        async with httpx.AsyncClient() as client:
            response = await client.get(raw_url)
            response.raise_for_status()
            code = response.text
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=400, detail=f"Error fetching code from GitHub: {e}")

    return await analyze_code(CodeRequest(code=code, github_link=request.github_link))

app.mount("/", StaticFiles(directory="api/ui", html=True), name="ui")