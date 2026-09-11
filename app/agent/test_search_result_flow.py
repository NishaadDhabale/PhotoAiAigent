import json

from agent.cli import extract_photo_results
from agent.conversation import ConversationManager
from agent.agent_runtime import invoke_agent
from agent.result_manager import PhotoResultManager
from photo_result import PhotoResult


# ------------------------------------------------------------
# Fake LangChain-style message
# ------------------------------------------------------------

class FakeMessage:
    def __init__(self, content):
        self.content = content


# ------------------------------------------------------------
# Fake agent
# ------------------------------------------------------------

class FakeAgent:
    """
    Simulates the LangChain agent without contacting Gemini.

    Each invocation returns the next configured response.
    """

    def __init__(self, responses):
        self.responses = responses
        self.calls = []
        self.index = 0

    def invoke(self, agent_input):
        self.calls.append(agent_input)

        if self.index >= len(self.responses):
            raise RuntimeError(
                "FakeAgent has no more configured responses."
            )

        response = self.responses[self.index]
        self.index += 1

        return response


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def make_photo(photo_id, similarity=0.9):
    return {
        "id": photo_id,
        "filename": f"photo_{photo_id}.jpg",
        "path": (
            f"D:/project/PhotoAgent/Images/"
            f"photo_{photo_id}.jpg"
        ),
        "date_taken": "2022-01-01 12:00:00",
        "camera": "Test Camera",
        "latitude": 19.0,
        "longitude": 73.0,
        "location_name": "Test Location",
        "similarity": similarity,
    }


def make_agent_response(photos, text="Mock response"):
    return {
        "messages": [
            FakeMessage(text),
            FakeMessage(
                json.dumps({
                    "count": len(photos),
                    "results": photos,
                })
            ),
        ]
    }


def process_search(
    agent,
    conversation,
    result_manager,
    query,
):
    """
    Simulates the natural-language search portion of CLI main().
    """

    conversation.add_user_message(query)

    response = invoke_agent(
        agent,
        conversation,
    )

    extracted_results = extract_photo_results(response)

    # Critical behavior:
    # latest search always replaces previous results.
    result_manager.set_results(
        extracted_results
    )

    messages = response.get("messages", [])

    if messages:
        answer = messages[-1].content
    else:
        answer = "I couldn't generate a response."

    conversation.add_assistant_message(answer)

    return response


# ------------------------------------------------------------
# Test 1: First search stores results
# ------------------------------------------------------------

def test_first_search_stores_results():

    agent = FakeAgent([
        make_agent_response([
            make_photo(1),
            make_photo(2),
            make_photo(3),
        ])
    ])

    conversation = ConversationManager()
    result_manager = PhotoResultManager()

    process_search(
        agent,
        conversation,
        result_manager,
        "Find outdoor photos",
    )

    assert len(result_manager) == 3

    results = result_manager.get_results()

    assert all(
        isinstance(photo, PhotoResult)
        for photo in results
    )

    assert [photo.id for photo in results] == [
        1,
        2,
        3,
    ]

    print("First search stores results: OK")


# ------------------------------------------------------------
# Test 2: Second search replaces first search
# ------------------------------------------------------------

def test_second_search_replaces_results():

    agent = FakeAgent([
        make_agent_response([
            make_photo(1),
            make_photo(2),
            make_photo(3),
        ]),
        make_agent_response([
            make_photo(10),
            make_photo(11),
        ]),
    ])

    conversation = ConversationManager()
    result_manager = PhotoResultManager()

    process_search(
        agent,
        conversation,
        result_manager,
        "Find outdoor photos",
    )

    assert [photo.id for photo in result_manager.get_results()] == [
        1,
        2,
        3,
    ]

    process_search(
        agent,
        conversation,
        result_manager,
        "Find photos of Nisha",
    )

    results = result_manager.get_results()

    assert len(results) == 2
    assert [photo.id for photo in results] == [
        10,
        11,
    ]

    print("Second search replaces results: OK")


# ------------------------------------------------------------
# Test 3: Empty search clears previous results
# ------------------------------------------------------------

def test_empty_search_clears_previous_results():

    agent = FakeAgent([
        make_agent_response([
            make_photo(1),
            make_photo(2),
        ]),
        make_agent_response([]),
    ])

    conversation = ConversationManager()
    result_manager = PhotoResultManager()

    process_search(
        agent,
        conversation,
        result_manager,
        "Find photos",
    )

    assert len(result_manager) == 2

    process_search(
        agent,
        conversation,
        result_manager,
        "Find photos from 1900",
    )

    assert len(result_manager) == 0
    assert result_manager.get_results() == []

    print("Empty search clears previous results: OK")


# ------------------------------------------------------------
# Test 4: Conversation survives result replacement
# ------------------------------------------------------------

def test_conversation_survives_result_replacement():

    agent = FakeAgent([
        make_agent_response([
            make_photo(1),
            make_photo(2),
        ]),
        make_agent_response([
            make_photo(5),
        ]),
    ])

    conversation = ConversationManager()
    result_manager = PhotoResultManager()

    process_search(
        agent,
        conversation,
        result_manager,
        "Find Nisha photos",
    )

    process_search(
        agent,
        conversation,
        result_manager,
        "Only from 2022",
    )

    messages = conversation.get_messages()

    assert len(messages) == 4

    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Find Nisha photos"

    assert messages[1]["role"] == "assistant"

    assert messages[2]["role"] == "user"
    assert messages[2]["content"] == "Only from 2022"

    assert messages[3]["role"] == "assistant"

    assert [photo.id for photo in result_manager.get_results()] == [
        5
    ]

    print("Conversation survives result replacement: OK")


# ------------------------------------------------------------
# Test 5: Result numbering follows latest search
# ------------------------------------------------------------

def test_result_numbering_uses_latest_results():

    agent = FakeAgent([
        make_agent_response([
            make_photo(1),
            make_photo(2),
            make_photo(3),
        ]),
        make_agent_response([
            make_photo(20),
            make_photo(21),
        ]),
    ])

    conversation = ConversationManager()
    result_manager = PhotoResultManager()

    process_search(
        agent,
        conversation,
        result_manager,
        "First search",
    )

    process_search(
        agent,
        conversation,
        result_manager,
        "Second search",
    )

    assert len(result_manager) == 2

    assert result_manager.get(1).id == 20
    assert result_manager.get(2).id == 21

    print("Result numbering uses latest search: OK")


# ------------------------------------------------------------
# Test 6: Similarity survives complete flow
# ------------------------------------------------------------

def test_similarity_survives_flow():

    agent = FakeAgent([
        make_agent_response([
            make_photo(50, similarity=0.981),
            make_photo(51, similarity=0.743),
        ])
    ])

    conversation = ConversationManager()
    result_manager = PhotoResultManager()

    process_search(
        agent,
        conversation,
        result_manager,
        "Find a beach",
    )

    results = result_manager.get_results()

    assert results[0].similarity == 0.981
    assert results[1].similarity == 0.743

    print("Similarity survives complete flow: OK")


# ------------------------------------------------------------
# Test 7: Agent receives accumulated conversation
# ------------------------------------------------------------

def test_agent_receives_accumulated_conversation():

    agent = FakeAgent([
        make_agent_response([
            make_photo(1),
        ]),
        make_agent_response([
            make_photo(2),
        ]),
        make_agent_response([
            make_photo(3),
        ]),
    ])

    conversation = ConversationManager()
    result_manager = PhotoResultManager()

    process_search(
        agent,
        conversation,
        result_manager,
        "Find photos of Nisha",
    )

    process_search(
        agent,
        conversation,
        result_manager,
        "Only from 2022",
    )

    process_search(
        agent,
        conversation,
        result_manager,
        "Only outdoor ones",
    )

    assert len(agent.calls) == 3

    first_messages = agent.calls[0]["messages"]
    second_messages = agent.calls[1]["messages"]
    third_messages = agent.calls[2]["messages"]

    assert len(first_messages) == 1
    assert len(second_messages) == 3
    assert len(third_messages) == 5

    assert (
        third_messages[0]["content"]
        == "Find photos of Nisha"
    )

    assert (
        third_messages[2]["content"]
        == "Only from 2022"
    )

    assert (
        third_messages[4]["content"]
        == "Only outdoor ones"
    )

    print("Agent receives accumulated conversation: OK")


# ------------------------------------------------------------
# Test 8: Clear creates completely fresh state
# ------------------------------------------------------------

def test_clear_creates_fresh_state():

    conversation = ConversationManager()
    result_manager = PhotoResultManager()

    conversation.add_user_message(
        "Find photos"
    )

    conversation.add_assistant_message(
        "Found photos."
    )

    result_manager.set_results([
        PhotoResult(
            id=1,
            filename="photo_1.jpg",
            path="D:/photo_1.jpg",
        )
    ])

    assert len(conversation) == 2
    assert len(result_manager) == 1

    conversation.clear()
    result_manager.clear()

    assert len(conversation) == 0
    assert len(result_manager) == 0

    assert conversation.get_messages() == []
    assert result_manager.get_results() == []

    print("Clear creates fresh state: OK")


# ------------------------------------------------------------
# Run grouped suite
# ------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("PhotoAgent Search → Result Flow Test")
    print("=" * 60)

    tests = [
        test_first_search_stores_results,
        test_second_search_replaces_results,
        test_empty_search_clears_previous_results,
        test_conversation_survives_result_replacement,
        test_result_numbering_uses_latest_results,
        test_similarity_survives_flow,
        test_agent_receives_accumulated_conversation,
        test_clear_creates_fresh_state,
    ]

    for test in tests:
        test()

    print()
    print("=" * 60)
    print("ALL SEARCH → RESULT FLOW TESTS PASSED")
    print("=" * 60)