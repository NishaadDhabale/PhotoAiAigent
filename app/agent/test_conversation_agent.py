from types import SimpleNamespace

from agent.conversation import ConversationManager
from agent.agent_runtime import (
    build_agent_input,
    invoke_agent,
)


# ------------------------------------------------------------
# Fake agent used for local testing
# ------------------------------------------------------------

class FakeAgent:
    def __init__(self):
        self.calls = []

    def invoke(self, agent_input):
        self.calls.append(agent_input)

        return {
            "messages": [
                SimpleNamespace(
                    content="Mock agent response."
                )
            ]
        }


# ------------------------------------------------------------
# Test 1: Empty conversation
# ------------------------------------------------------------

def test_empty_conversation():

    conversation = ConversationManager()

    assert conversation.is_empty()
    assert len(conversation) == 0
    assert conversation.get_messages() == []

    print("Empty conversation: OK")


# ------------------------------------------------------------
# Test 2: User message
# ------------------------------------------------------------

def test_user_message():

    conversation = ConversationManager()

    conversation.add_user_message(
        "Find photos of Nisha"
    )

    messages = conversation.get_messages()

    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Find photos of Nisha"

    print("User message: OK")


# ------------------------------------------------------------
# Test 3: User + assistant conversation
# ------------------------------------------------------------

def test_user_assistant_conversation():

    conversation = ConversationManager()

    conversation.add_user_message(
        "Find photos of Nisha"
    )

    conversation.add_assistant_message(
        "I found 5 photos."
    )

    messages = conversation.get_messages()

    assert len(messages) == 2

    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"

    assert messages[0]["content"] == "Find photos of Nisha"
    assert messages[1]["content"] == "I found 5 photos."

    print("User + assistant conversation: OK")


# ------------------------------------------------------------
# Test 4: Conversation order
# ------------------------------------------------------------

def test_conversation_order():

    conversation = ConversationManager()

    conversation.add_user_message("Find Nisha photos")
    conversation.add_assistant_message("Found 5 photos.")
    conversation.add_user_message("Only from 2022")
    conversation.add_assistant_message("Found 2 photos.")

    messages = conversation.get_messages()

    assert len(messages) == 4

    assert messages[0]["content"] == "Find Nisha photos"
    assert messages[1]["content"] == "Found 5 photos."
    assert messages[2]["content"] == "Only from 2022"
    assert messages[3]["content"] == "Found 2 photos."

    print("Conversation order: OK")


# ------------------------------------------------------------
# Test 5: Conversation is copied safely
# ------------------------------------------------------------

def test_conversation_copy_isolation():

    conversation = ConversationManager()

    conversation.add_user_message("Find photos")

    messages = conversation.get_messages()

    messages.append({
        "role": "user",
        "content": "Injected message"
    })

    assert len(conversation) == 1

    print("Conversation copy isolation: OK")


# ------------------------------------------------------------
# Test 6: Empty/invalid user messages rejected
# ------------------------------------------------------------

def test_invalid_user_messages():

    conversation = ConversationManager()

    try:
        conversation.add_user_message("")
        assert False, "Expected ValueError"
    except ValueError:
        pass

    try:
        conversation.add_user_message("   ")
        assert False, "Expected ValueError"
    except ValueError:
        pass

    try:
        conversation.add_user_message(None)
        assert False, "Expected TypeError"
    except TypeError:
        pass

    print("Invalid user messages: OK")


# ------------------------------------------------------------
# Test 7: Empty/invalid assistant messages rejected
# ------------------------------------------------------------

def test_invalid_assistant_messages():

    conversation = ConversationManager()

    try:
        conversation.add_assistant_message("")
        assert False, "Expected ValueError"
    except ValueError:
        pass

    try:
        conversation.add_assistant_message("   ")
        assert False, "Expected ValueError"
    except ValueError:
        pass

    try:
        conversation.add_assistant_message(None)
        assert False, "Expected TypeError"
    except TypeError:
        pass

    print("Invalid assistant messages: OK")


# ------------------------------------------------------------
# Test 8: Build LangChain agent input
# ------------------------------------------------------------

def test_build_agent_input():

    conversation = ConversationManager()

    conversation.add_user_message(
        "Find photos of Nisha"
    )

    conversation.add_assistant_message(
        "I found 5 photos."
    )

    conversation.add_user_message(
        "Only from 2022"
    )

    agent_input = build_agent_input(conversation)

    assert isinstance(agent_input, dict)
    assert "messages" in agent_input

    assert len(agent_input["messages"]) == 3

    assert agent_input["messages"][0]["role"] == "user"
    assert agent_input["messages"][1]["role"] == "assistant"
    assert agent_input["messages"][2]["role"] == "user"

    assert (
        agent_input["messages"][2]["content"]
        == "Only from 2022"
    )

    print("Agent input construction: OK")


# ------------------------------------------------------------
# Test 9: Agent receives complete conversation
# ------------------------------------------------------------

def test_agent_receives_conversation():

    conversation = ConversationManager()

    conversation.add_user_message(
        "Find photos of Nisha"
    )

    conversation.add_assistant_message(
        "I found 5 photos."
    )

    conversation.add_user_message(
        "Only from 2022"
    )

    fake_agent = FakeAgent()

    response = invoke_agent(
        fake_agent,
        conversation,
    )

    assert response is not None

    assert len(fake_agent.calls) == 1

    received = fake_agent.calls[0]

    assert "messages" in received
    assert len(received["messages"]) == 3

    assert (
        received["messages"][0]["content"]
        == "Find photos of Nisha"
    )

    assert (
        received["messages"][2]["content"]
        == "Only from 2022"
    )

    print("Agent receives conversation: OK")


# ------------------------------------------------------------
# Test 10: Clear resets conversation
# ------------------------------------------------------------

def test_clear_conversation():

    conversation = ConversationManager()

    conversation.add_user_message("Find Nisha")
    conversation.add_assistant_message("Found 5 photos.")

    assert len(conversation) == 2

    conversation.clear()

    assert len(conversation) == 0
    assert conversation.is_empty()
    assert conversation.get_messages() == []

    print("Conversation clear: OK")


# ------------------------------------------------------------
# Test 11: Last message
# ------------------------------------------------------------

def test_last_message():

    conversation = ConversationManager()

    assert conversation.last_message() is None

    conversation.add_user_message(
        "Find outdoor photos"
    )

    last = conversation.last_message()

    assert last["role"] == "user"
    assert last["content"] == "Find outdoor photos"

    conversation.add_assistant_message(
        "I found 10 photos."
    )

    last = conversation.last_message()

    assert last["role"] == "assistant"
    assert last["content"] == "I found 10 photos."

    print("Last message: OK")


# ------------------------------------------------------------
# Run grouped suite
# ------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("PhotoAgent Conversation Agent Test")
    print("=" * 60)

    tests = [
        test_empty_conversation,
        test_user_message,
        test_user_assistant_conversation,
        test_conversation_order,
        test_conversation_copy_isolation,
        test_invalid_user_messages,
        test_invalid_assistant_messages,
        test_build_agent_input,
        test_agent_receives_conversation,
        test_clear_conversation,
        test_last_message,
    ]

    for test in tests:
        test()

    print()
    print("=" * 60)
    print("ALL CONVERSATION AGENT TESTS PASSED")
    print("=" * 60)