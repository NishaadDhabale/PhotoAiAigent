import os

from dotenv import load_dotenv

from agent import create_photo_agent
from agent.cli import extract_text


load_dotenv()


def run_agent_query(agent, query):
    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": query,
                }
            ]
        }
    )

    return response, extract_text(response)


def test_response_extraction():
    print("Test 1: Response extraction")

    # Plain string
    response = {
        "messages": [
            type(
                "Message",
                (),
                {"content": "Hello PhotoAgent"}
            )()
        ]
    }

    assert extract_text(response) == "Hello PhotoAgent"

    # Gemini-style content blocks
    response = {
        "messages": [
            type(
                "Message",
                (),
                {
                    "content": [
                        {
                            "type": "text",
                            "text": "First part",
                            "extras": {
                                "signature": "internal-signature"
                            },
                        },
                        {
                            "type": "text",
                            "text": "Second part",
                        },
                    ]
                },
            )()
        ]
    }

    result = extract_text(response)

    assert result == "First part\nSecond part"
    assert "internal-signature" not in result

    print("Response extraction: OK")


def test_api_key():
    print("\nTest 2: Gemini API key")

    api_key = os.getenv("GOOGLE_API_KEY")

    assert api_key
    assert api_key.strip()

    print("GOOGLE_API_KEY exists: OK")


def test_agent_creation():
    print("\nTest 3: Agent creation")

    agent = create_photo_agent()

    assert agent is not None

    print("Agent creation: OK")

    return agent


def test_structured_search(agent):
    print("\nTest 4: Structured search")

    response, text = run_agent_query(
        agent,
        "Show me photos from 2022",
    )

    assert text
    assert "2022" in text

    print("Agent response:")
    print(text)

    print("\nStructured search: OK")


def test_person_search(agent):
    print("\nTest 5: Person search")

    response, text = run_agent_query(
        agent,
        "Show me photos of Nisha",
    )

    assert text
    assert "Nisha" in text

    print("Agent response:")
    print(text)

    print("\nPerson search: OK")


def test_semantic_search(agent):
    print("\nTest 6: Semantic search")

    response, text = run_agent_query(
        agent,
        "Find photos showing an outdoor scene",
    )

    assert text

    print("Agent response:")
    print(text)

    print("\nSemantic search: OK")


def test_hybrid_search(agent):
    print("\nTest 7: Hybrid search")

    response, text = run_agent_query(
        agent,
        "Find photos of Nisha from 2022",
    )

    assert text
    assert "Nisha" in text
    assert "2022" in text

    print("Agent response:")
    print(text)

    print("\nHybrid search: OK")


def main():
    print("=" * 60)
    print("PhotoAgent CLI + Gemini Agent Test")
    print("=" * 60)

    test_response_extraction()
    test_api_key()

    agent = test_agent_creation()

    test_structured_search(agent)
    test_person_search(agent)
    test_semantic_search(agent)
    test_hybrid_search(agent)

    print("\n" + "=" * 60)
    print("ALL CLI + GEMINI AGENT TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()