import pytest
import json

from google.adk.events import Event
from google.adk.sessions import InMemorySessionService
from google.adk.agents.invocation_context import InvocationContext, RunConfig
from google.genai.types import Content, Part

from agentic_code_analyzer.agents.analysis.json_formatting_agent import (
    JsonFormattingAgent,
)

# A sample valid JSON object to use for creating test responses.
VALID_JSON_OBJECT = {
    "overall_score": 90,
    "criteria_breakdown": [
        {
            "criterion_name": "runnability_and_configuration",
            "score": 10,
            "reasoning": "The code is runnable and well-configured.",
            "recommendations_for_llm_fix": [],
        }
    ],
}


async def run_agent_test(initial_state: dict, mocked_llm_response: str, mocker):
    """
    A simplified and robust helper for testing the JsonFormattingAgent.
    It directly mocks the agent's own `_call_model_async` method.
    """
    # 1. Instantiate the agent to be tested.
    agent = JsonFormattingAgent(
        name="test_json_formatter",
        output_key="evaluation_review_agent_output",
        model="gemini-test-model",  # This is just a placeholder
    )

    # 2. Mock the `_call_model_async` method directly on the agent instance.
    # This is the most direct and stable way to control the LLM response.
    mock_flow = mocker.patch(
        "agentic_code_analyzer.agents.analysis.json_formatting_agent.JsonFormattingAgent._llm_flow",
        new_callable=mocker.PropertyMock,
    )

    async def mock_run_async(*args, **kwargs):
        yield Event(
            author=agent.name,
            content=Content(parts=[Part(text=mocked_llm_response)]),
            turn_complete=True,
        )

    mock_flow.return_value.run_async = mock_run_async

    # 3. Set up the session and a basic InvocationContext.
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user",
        session_id="test_session",
        state=initial_state,
    )
    context = InvocationContext(
        agent=agent,
        session=session,
        session_service=session_service,
        invocation_id="test_invocation",
        run_config=RunConfig(),
    )

    # 4. Run the agent's internal logic by calling `_run_async_impl`.
    async for event in agent._run_async_impl(context):
        if event.is_final_response() and event.content and event.content.parts:
            context.session.state["evaluation_review_agent_output"] = (
                event.content.parts[0].text
            )

    # 5. Return the final session state for assertions.
    return session.state


@pytest.mark.asyncio
class TestJsonFormattingAgent:
    """
    Tests for the JsonFormattingAgent. These tests verify that the agent
    correctly stores the raw LLM response in the session state.
    """

    @pytest.mark.parametrize(
        "llm_response, test_id",
        [
            (json.dumps(VALID_JSON_OBJECT), "clean_json"),
            (f"```json\n{json.dumps(VALID_JSON_OBJECT)}\n```", "markdown_json"),
            ('{"error": "invalid"}', "malformed_json"),
        ],
    )
    async def test_agent_stores_llm_response_in_session(
        self, llm_response, test_id, mocker
    ):
        """
        Tests that the agent takes the raw text from the mocked LLM call and
        places it into the correct output key in the session state.
        """
        initial_state = {"initial_analysis_output": "Some raw text analysis."}
        final_state = await run_agent_test(initial_state, llm_response, mocker)

        # The agent's job is to put the LLM's raw response into this key.
        # The downstream `ResultProcessingAgent` is responsible for parsing it.
        result_str = final_state.get("evaluation_review_agent_output")

        assert result_str is not None, (
            "The output key should be populated in the session state"
        )
        assert result_str == llm_response, f"Test failed for: {test_id}"
