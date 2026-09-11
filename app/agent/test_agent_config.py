from agent.agent import (
    SYSTEM_PROMPT,
    create_photo_agent,
)
from agent.tools import PHOTO_SEARCH_TOOLS


def test_system_prompt():
    print("Test 1: System prompt")

    assert isinstance(SYSTEM_PROMPT, str)
    assert len(SYSTEM_PROMPT) > 500

    required_phrases = [
        "structured_photo_search",
        "semantic_photo_search",
        "hybrid_photo_search",
        "READ-ONLY",
        "Never invent",
        "conversation history",
    ]

    for phrase in required_phrases:
        assert phrase in SYSTEM_PROMPT

    print("System prompt: OK")


def test_api_key_configuration():
    print("\nTest 2: API key configuration")

    import os

    api_key = os.getenv("GOOGLE_API_KEY")

    assert api_key is not None
    assert api_key.strip() != ""

    print("API key configuration: OK")


def test_agent_creation():
    print("\nTest 3: Agent creation")

    agent = create_photo_agent()

    assert agent is not None

    print("Agent creation: OK")


def test_agent_tools():
    print("\nTest 4: Agent tools")

    tool_names = {
        tool.name
        for tool in PHOTO_SEARCH_TOOLS
    }

    assert "structured_photo_search" in tool_names
    assert "semantic_photo_search" in tool_names
    assert "hybrid_photo_search" in tool_names

    assert len(tool_names) == 3

    print("Agent tools: OK")


def test_agent_is_read_only():
    print("\nTest 5: Read-only agent")

    tool_names = {
        tool.name
        for tool in PHOTO_SEARCH_TOOLS
    }

    forbidden_tools = {
        "delete_photo",
        "move_photo",
        "rename_photo",
        "copy_photo",
        "modify_photo",
    }

    assert tool_names.isdisjoint(forbidden_tools)

    assert "READ-ONLY" in SYSTEM_PROMPT

    print("Read-only contract: OK")


def test_tool_descriptions():
    print("\nTest 6: Tool descriptions")

    descriptions = {
        tool.name: tool.description
        for tool in PHOTO_SEARCH_TOOLS
    }

    assert "structured_photo_search" in descriptions
    assert "semantic_photo_search" in descriptions
    assert "hybrid_photo_search" in descriptions

    assert descriptions["structured_photo_search"]
    assert descriptions["semantic_photo_search"]
    assert descriptions["hybrid_photo_search"]

    print("Tool descriptions: OK")


def main():
    print("=" * 60)
    print("PhotoAgent Agent Configuration Test")
    print("=" * 60)

    test_system_prompt()
    test_api_key_configuration()
    test_agent_creation()
    test_agent_tools()
    test_agent_is_read_only()
    test_tool_descriptions()

    print("\n" + "=" * 60)
    print("ALL AGENT CONFIGURATION TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()