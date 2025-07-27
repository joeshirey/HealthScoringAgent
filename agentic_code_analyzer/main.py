import asyncio
import json
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agentic_code_analyzer.orchestrator import CodeAnalyzerOrchestrator
from dotenv import load_dotenv

load_dotenv()


async def main():
    """Runs the agentic code analyzer."""
    try:
        with open("sample.py", "r") as f:
            code_snippet = f.read()
        if not code_snippet:
            print("Error: sample.py is empty.")
            return
    except FileNotFoundError:
        print("Error: sample.py not found.")
        return
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="agentic_code_analyzer",
        user_id="test_user",
        session_id="test_session",
        state={
            "code_snippet": code_snippet,
            "github_link": "https://github.com/GoogleCloudPlatform/python-docs-samples/blob/main/storage/control/storage_control_get_project_intelligence_config.py",
        },
    )

    runner = Runner(
        agent=CodeAnalyzerOrchestrator(name="code_analyzer_orchestrator"),
        app_name="agentic_code_analyzer",
        session_service=session_service,
    )

    final_response = ""
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session",
        new_message=types.Content(parts=[types.Part(text=code_snippet)]),
    ):
        if event.is_final_response():
            final_response = event.content.parts[0].text

    print(json.dumps(json.loads(final_response), indent=4))


if __name__ == "__main__":
    asyncio.run(main())
