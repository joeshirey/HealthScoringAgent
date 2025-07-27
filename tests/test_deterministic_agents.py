import pytest
from google.adk.sessions import InMemorySessionService
from google.adk.agents.invocation_context import InvocationContext

from agentic_code_analyzer.agents.deterministic_language_detection_agent import (
    DeterministicLanguageDetectionAgent,
)
from agentic_code_analyzer.agents.deterministic_region_tag_agent import (
    DeterministicRegionTagAgent,
)


# Helper function to run an agent and get the final event
async def run_agent_and_get_event(agent, state):
    """
    A helper function to set up and run an agent's implementation with a
    given state, and return the resulting session for inspection.
    """
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user",
        session_id="test_session",
        state=state,
    )
    context = InvocationContext(
        agent=agent,
        session=session,
        session_service=session_service,
        invocation_id="test_invocation",
    )
    # The deterministic agents in this test don't yield multiple events,
    # but we iterate to be consistent with the async generator pattern.
    async for _ in agent._run_async_impl(context):
        pass  # We only care about the final state of the session

    return session


@pytest.mark.asyncio
class TestDeterministicLanguageDetectionAgent:
    """
    Tests for the DeterministicLanguageDetectionAgent.
    """

    @pytest.mark.parametrize(
        "code, expected_language, test_id",
        [
            # Python: Specific `def` with colon to distinguish from Ruby
            (
                "def hello_world(self):\n    print('Hello, Python!')",
                "Python",
                "python_simple",
            ),
            # Java: Standard class definition
            (
                'public class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println("Hello, Java!");\n    }\n}',
                "Java",
                "java_simple",
            ),
            # Javascript: Using `const` and `console.log` for high confidence
            (
                "const x = () => {\n  console.log('Hello, JavaScript!');\n};",
                "Javascript",
                "javascript_simple",
            ),
            # Ruby: Specific `def` without parentheses/colon and `puts`
            ("def hello_ruby\n  puts 'Hello, Ruby!'\nend", "Ruby", "ruby_simple"),
            # C#: Using `namespace` to differentiate from Java
            (
                "namespace MyWebApp.Models\n{\n    public class ErrorViewModel\n    {\n        public string RequestId { get; set; }\n\n        public bool ShowRequestId => !string.IsNullOrEmpty(RequestId);\n    }\n}",
                "C#",
                "csharp_simple",
            ),
            # C++: Using `#include` and `std::` to differentiate
            (
                '#include <iostream>\nint main() {\n    std::cout << "Hello, C++!";\n    return 0;\n}',
                "C++",
                "cpp_simple",
            ),
            # Code that should not match any specific language
            ("a + b", "Unknown", "unknown_code"),
            # Empty string should be unknown
            ("", "Unknown", "empty_string"),
        ],
    )
    async def test_language_detection(self, code, expected_language, test_id):
        """
        Tests that the agent correctly detects the language of a code snippet
        and updates the session state.
        """
        agent = DeterministicLanguageDetectionAgent(name="lang_detect_test")
        initial_state = {"code_snippet": code}

        session = await run_agent_and_get_event(agent, initial_state)

        detected_language = session.state.get("language_detection_agent_output")
        assert detected_language == expected_language, f"Test failed for {test_id}"


@pytest.mark.asyncio
class TestDeterministicRegionTagAgent:
    """
    Tests for the DeterministicRegionTagAgent.
    """

    @pytest.mark.parametrize(
        "code, expected_tags_str, test_id",
        [
            (
                "# [START storage_control_get_project_intelligence_config]",
                "storage_control_get_project_intelligence_config",
                "python_single_tag",
            ),
            (
                "// [START some_other_tag]\n// [END some_other_tag]",
                "some_other_tag",
                "js_single_tag",
            ),
            (
                "/* [START one_tag] */\n...code...\n/* [START another_tag] */",
                "one_tag,another_tag",
                "multiple_tags_different_styles",
            ),
            (
                "# [START vision_product_search_create_product]\n# [START vision_product_search_list_products]",
                "vision_product_search_create_product,vision_product_search_list_products",
                "python_multiple_tags",
            ),
            ("no tags here", "", "no_tags"),
            ("", "", "empty_string"),
        ],
    )
    async def test_region_tag_extraction(self, code, expected_tags_str, test_id):
        """
        Tests that the agent correctly extracts region tags from a code snippet
        and updates the session state.
        """
        agent = DeterministicRegionTagAgent(name="region_tag_test")
        initial_state = {"code_snippet": code}

        session = await run_agent_and_get_event(agent, initial_state)

        extracted_tags_str = session.state.get("region_tag_extraction_agent_output")

        # Sort both actual and expected tags for deterministic comparison
        actual_tags = (
            sorted(extracted_tags_str.split(",")) if extracted_tags_str else []
        )
        expected_tags = (
            sorted(expected_tags_str.split(",")) if expected_tags_str else []
        )

        assert actual_tags == expected_tags, f"Test failed for {test_id}"
