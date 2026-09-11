from agent.cli import handle_local_command
from agent.conversation import ConversationManager
from agent.result_manager import PhotoResultManager
from agent.agent_runtime import invoke_agent
from photo_result import PhotoResult


class FakeAgent:
    """
    Fake LangChain-style agent.

    It records the conversation it receives and returns
    a deterministic response without calling Gemini.
    """

    def __init__(self):
        self.calls = []

    def invoke(self, agent_input):
        self.calls.append(agent_input)

        return {
            "messages": [
                type(
                    "FakeMessage",
                    (),
                    {
                        "content": "Mock response"
                    },
                )()
            ]
        }


def make_photo(photo_id):
    return PhotoResult(
        id=photo_id,
        filename=f"photo_{photo_id}.jpg",
        path=(
            f"D:/project/PhotoAgent/Images/"
            f"photo_{photo_id}.jpg"
        ),
        date_taken="2022-01-01 12:00:00",
        camera="Test Camera",
        latitude=19.0,
        longitude=73.0,
        location_name="Test Location",
        similarity=0.9,
    )
# ------------------------------------------------------------
# Test 1: Agent receives first user message
# ------------------------------------------------------------

def test_first_message_reaches_agent():

    conversation = ConversationManager()
    agent = FakeAgent()

    conversation.add_user_message(
        "Find photos of Nisha"
    )

    response = invoke_agent(
        agent,
        conversation,
    )

    assert response is not None
    assert len(agent.calls) == 1

    messages = agent.calls[0]["messages"]

    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Find photos of Nisha"

    print("First message reaches agent: OK")


# ------------------------------------------------------------
# Test 2: Follow-up receives previous conversation
# ------------------------------------------------------------

def test_followup_receives_history():

    conversation = ConversationManager()
    agent = FakeAgent()

    conversation.add_user_message(
        "Find photos of Nisha"
    )

    conversation.add_assistant_message(
        "I found 5 photos."
    )

    conversation.add_user_message(
        "Only from 2022"
    )

    invoke_agent(
        agent,
        conversation,
    )

    messages = agent.calls[0]["messages"]

    assert len(messages) == 3

    assert messages[0]["content"] == "Find photos of Nisha"
    assert messages[1]["content"] == "I found 5 photos."
    assert messages[2]["content"] == "Only from 2022"

    print("Follow-up receives history: OK")


# ------------------------------------------------------------
# Test 3: Multiple turns preserve order
# ------------------------------------------------------------

def test_multiple_turn_order():

    conversation = ConversationManager()
    agent = FakeAgent()

    conversation.add_user_message("Find outdoor photos")
    conversation.add_assistant_message("Found 10 photos.")
    conversation.add_user_message("Only from 2022")
    conversation.add_assistant_message("Found 6 photos.")
    conversation.add_user_message("Only Nisha")

    invoke_agent(
        agent,
        conversation,
    )

    messages = agent.calls[0]["messages"]

    expected = [
        ("user", "Find outdoor photos"),
        ("assistant", "Found 10 photos."),
        ("user", "Only from 2022"),
        ("assistant", "Found 6 photos."),
        ("user", "Only Nisha"),
    ]

    actual = [
        (message["role"], message["content"])
        for message in messages
    ]

    assert actual == expected

    print("Multiple-turn order: OK")


# ------------------------------------------------------------
# Test 4: Local clear command clears everything
# ------------------------------------------------------------

def test_clear_clears_conversation_and_results():

    conversation = ConversationManager()
    result_manager = PhotoResultManager()

    conversation.add_user_message(
        "Find photos"
    )

    conversation.add_assistant_message(
        "Found photos."
    )

    result_manager.set_results([
        make_photo(1),
        make_photo(2),
    ])

    assert len(conversation) == 2
    assert len(result_manager) == 2

    handled = handle_local_command(
        "clear",
        result_manager,
        conversation,
    )

    assert handled is True
    assert len(conversation) == 0
    assert len(result_manager) == 0

    print("Clear resets conversation and results: OK")


# ------------------------------------------------------------
# Test 5: Local list command does not modify conversation
# ------------------------------------------------------------

def test_list_does_not_modify_conversation():

    conversation = ConversationManager()
    result_manager = PhotoResultManager()

    conversation.add_user_message(
        "Find photos"
    )

    conversation.add_assistant_message(
        "Found photos."
    )

    result_manager.set_results([
        make_photo(1),
        make_photo(2),
    ])

    before = conversation.get_messages()

    handled = handle_local_command(
        "list",
        result_manager,
        conversation,
    )

    after = conversation.get_messages()

    assert handled is True
    assert before == after
    assert len(result_manager) == 2

    print("List preserves conversation: OK")


# ------------------------------------------------------------
# Test 6: Unknown command is not handled locally
# ------------------------------------------------------------

def test_unknown_command():

    conversation = ConversationManager()
    result_manager = PhotoResultManager()

    handled = handle_local_command(
        "find outdoor photos",
        result_manager,
        conversation,
    )

    assert handled is False

    print("Natural-language command passes through: OK")


# ------------------------------------------------------------
# Test 7: Open command is handled locally
# ------------------------------------------------------------

def test_open_command_is_local():

    conversation = ConversationManager()
    result_manager = PhotoResultManager()

    result_manager.set_results([
        make_photo(1),
    ])

    # We only verify command routing here.
    # The actual OS image opening is tested separately
    # by test_photo_open.py.

    import agent.cli

    original_open = agent.cli.open_photo

    opened = []

    def fake_open(photo):
        opened.append(photo)

    agent.cli.open_photo = fake_open

    try:
        handled = handle_local_command(
            "open 1",
            result_manager,
            conversation,
        )
    finally:
        agent.cli.open_photo = original_open

    assert handled is True
    assert len(opened) == 1
    assert opened[0].id == 1

    print("Open command handled locally: OK")


# ------------------------------------------------------------
# Test 8: Agent invocation does not mutate conversation
# ------------------------------------------------------------

def test_invoke_does_not_mutate_conversation():

    conversation = ConversationManager()
    agent = FakeAgent()

    conversation.add_user_message(
        "Find photos"
    )

    before = conversation.get_messages()

    invoke_agent(
        agent,
        conversation,
    )

    after = conversation.get_messages()

    assert before == after

    print("Agent invocation preserves conversation: OK")


# ------------------------------------------------------------
# Run grouped suite
# ------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("PhotoAgent CLI Runtime Integration Test")
    print("=" * 60)

    tests = [
        test_first_message_reaches_agent,
        test_followup_receives_history,
        test_multiple_turn_order,
        test_clear_clears_conversation_and_results,
        test_list_does_not_modify_conversation,
        test_unknown_command,
        test_open_command_is_local,
        test_invoke_does_not_mutate_conversation,
    ]

    for test in tests:
        test()

    print()
    print("=" * 60)
    print("ALL CLI RUNTIME TESTS PASSED")
    print("=" * 60)