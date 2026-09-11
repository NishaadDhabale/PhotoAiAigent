from agent.conversation import ConversationManager


def build_agent_input(conversation):
    """
    Convert ConversationManager state into the input format
    expected by LangChain create_agent().
    """

    if not isinstance(conversation, ConversationManager):
        raise TypeError(
            "conversation must be a ConversationManager."
        )

    messages = conversation.get_messages()

    return {
        "messages": messages
    }


def invoke_agent(agent, conversation):
    """
    Invoke the LangChain agent using the current conversation.
    """

    if agent is None:
        raise ValueError("agent cannot be None.")

    agent_input = build_agent_input(conversation)

    return agent.invoke(agent_input)