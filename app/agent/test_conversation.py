from agent.conversation import ConversationManager


def test_empty_conversation():
    print("Test 1: Empty conversation")

    conversation = ConversationManager()

    assert len(conversation) == 0
    assert conversation.get_messages() == []

    print("Empty conversation: OK")


def test_user_message():
    print("\nTest 2: User message")

    conversation = ConversationManager()

    conversation.add_user_message(
        "Show me photos of Nisha"
    )

    messages = conversation.get_messages()

    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Show me photos of Nisha"

    print("User message: OK")


def test_conversation_order():
    print("\nTest 3: Conversation order")

    conversation = ConversationManager()

    conversation.add_user_message(
        "Show me photos of Nisha"
    )

    conversation.add_assistant_message(
        "I found 5 photos of Nisha."
    )

    conversation.add_user_message(
        "Only from 2022"
    )

    messages = conversation.get_messages()

    assert len(messages) == 3

    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"
    assert messages[2]["role"] == "user"

    assert messages[0]["content"] == (
        "Show me photos of Nisha"
    )

    assert messages[2]["content"] == (
        "Only from 2022"
    )

    print("Conversation order: OK")


def test_history_isolation():
    print("\nTest 4: History isolation")

    conversation = ConversationManager()

    conversation.add_user_message(
        "Show me photos"
    )

    messages = conversation.get_messages()

    messages.clear()

    # Clearing the returned list must not clear
    # the actual conversation.
    assert len(conversation) == 1

    print("History isolation: OK")


def test_clear():
    print("\nTest 5: Clear conversation")

    conversation = ConversationManager()

    conversation.add_user_message(
        "Show me photos of Nisha"
    )

    conversation.add_assistant_message(
        "I found 5 photos."
    )

    assert len(conversation) == 2

    conversation.clear()

    assert len(conversation) == 0
    assert conversation.get_messages() == []

    print("Clear conversation: OK")


def test_follow_up_context():
    print("\nTest 6: Follow-up context")

    conversation = ConversationManager()

    conversation.add_user_message(
        "Show me photos of Nisha"
    )

    conversation.add_assistant_message(
        "I found 5 photos of Nisha."
    )

    conversation.add_user_message(
        "Only from 2022"
    )

    messages = conversation.get_messages()

    # The important property is that the follow-up
    # exists together with the previous conversation.
    assert messages[-1]["content"] == "Only from 2022"
    assert messages[-3]["content"] == (
        "Show me photos of Nisha"
    )

    print("Follow-up context: OK")


def main():
    print("=" * 60)
    print("PhotoAgent Conversation Manager Test")
    print("=" * 60)

    test_empty_conversation()
    test_user_message()
    test_conversation_order()
    test_history_isolation()
    test_clear()
    test_follow_up_context()

    print("\n" + "=" * 60)
    print("ALL CONVERSATION TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()