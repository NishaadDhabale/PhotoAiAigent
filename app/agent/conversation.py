class ConversationManager:
    """
    Maintains the current PhotoAgent conversation.

    Conversation state is session-local and is not persisted.
    """

    def __init__(self):
        self._messages = []

    def add_user_message(self, content):
        if not isinstance(content, str):
            raise TypeError("User message must be a string.")

        content = content.strip()

        if not content:
            raise ValueError("User message cannot be empty.")

        self._messages.append({
            "role": "user",
            "content": content,
        })

    def add_assistant_message(self, content):
        if not isinstance(content, str):
            raise TypeError("Assistant message must be a string.")

        content = content.strip()

        if not content:
            raise ValueError("Assistant message cannot be empty.")

        self._messages.append({
            "role": "assistant",
            "content": content,
        })

    def get_messages(self):
        """
        Return a copy so callers cannot mutate internal state.
        """
        return list(self._messages)

    def clear(self):
        self._messages.clear()

    def is_empty(self):
        return len(self._messages) == 0

    def last_message(self):
        if not self._messages:
            return None

        return self._messages[-1]

    def __len__(self):
        return len(self._messages)