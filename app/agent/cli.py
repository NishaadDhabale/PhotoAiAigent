import ast
import json

from agent.agent_runtime import invoke_agent
from agent.conversation import ConversationManager
from agent import create_photo_agent
from photo_access import open_photo
from photo_result import PhotoResult
from agent.result_manager import PhotoResultManager
from agent.result_normalizer import normalize_photo_dict


def extract_text(response):
    messages = response.get("messages", [])

    if not messages:
        return "I couldn't generate a response."

    content = messages[-1].content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []

        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    text = block.get("text")

                    if text:
                        text_parts.append(text)

            elif isinstance(block, str):
                text_parts.append(block)

        if text_parts:
            return "\n".join(text_parts)

    return str(content)


def _parse_tool_content(content):
    if isinstance(content, (dict, list)):
        return content

    if not isinstance(content, str):
        return None

    content = content.strip()

    if not content:
        return None

    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError):
        pass

    try:
        return ast.literal_eval(content)
    except (ValueError, SyntaxError):
        pass

    return None


def _collect_photo_dicts(value, results):
    if isinstance(value, dict):
        has_id = "id" in value or "photo_id" in value

        if (
            has_id
            and "filename" in value
            and "path" in value
        ):
            results.append(value)

        for child in value.values():
            _collect_photo_dicts(child, results)

    elif isinstance(value, list):
        for child in value:
            _collect_photo_dicts(child, results)



def extract_photo_results(response):
    """
    Extract photo records from LangChain tool messages.
    """

    messages = response.get("messages", [])

    raw_results = []

    for message in messages:

        content = getattr(message, "content", None)

        if content is None:
            continue

        parsed = _parse_tool_content(content)

        if parsed is not None:
            _collect_photo_dicts(parsed, raw_results)

    unique = {}

    for row in raw_results:
        try:
            normalized = normalize_photo_dict(row)
        except (TypeError, ValueError):
            continue

        photo_id = normalized["id"]
        unique[photo_id] = normalized

    return [
        PhotoResult(
            id=int(row["id"]),
            filename=row["filename"],
            path=row["path"],
            date_taken=row.get("date_taken"),
            camera=row.get("camera"),
            latitude=row.get("latitude"),
            longitude=row.get("longitude"),
            location_name=row.get("location_name"),
            similarity=row.get("similarity"),
        )
        for row in unique.values()
    ]


def print_photo_list(photos):
    if not photos:
        print("No photo results available.")
        return

    print()
    print("Available photos:")

    for index, photo in enumerate(photos, start=1):
        print(f"[{index}] {photo.filename}")

    print()


def handle_local_command(command, result_manager,conversation,
):
    """
    Handle commands that must remain completely local.

    Returns True if the command was handled locally.
    """

    command = command.strip()

    if not command:
        return True

    lower = command.lower()

    # ---------------------------------------------------------
    # OPEN
    # ---------------------------------------------------------

    if lower.startswith("open "):

        value = command[5:].strip()

        try:
            number = int(value)
        except ValueError:
            print("Usage: open <number>")
            return True

        if len(result_manager) == 0:
            print("There are no photo results to open.")
            print("Run a photo search first.")
            return True

        try:
            photo = result_manager.get(number)

        except IndexError as exc:
            print(exc)
            return True

        try:
            open_photo(photo)
            print(f"Opening {photo.filename}...")

        except FileNotFoundError as exc:
            print(f"Photo not found: {exc}")

        except Exception as exc:
            print(f"Could not open photo: {exc}")

        return True

    # ---------------------------------------------------------
    # LIST
    # ---------------------------------------------------------

    if lower == "list":

        photos = result_manager.get_results()

        if not photos:
            print("There are no photo results yet.")
        else:
            print_photo_list(photos)

        return True



# ---------------------------------------------------------
# CLEAR CONVERSATION
# ---------------------------------------------------------

    if lower == "clear":
        result_manager.clear()
        conversation.clear()

        print("Conversation and current photo results cleared.")

        return True
    return False


def main():

    print("=" * 60)
    print("📸 PhotoAgent")
    print("=" * 60)
    print("Your local-first AI photo assistant.")
    print()
    print("Ask questions about your photos.")
    print()
    print("Local commands:")
    print("  open <number>  Open a photo from the last search")
    print("  list           List the last search results")
    print("  clear          Start a new conversation")
    print("  exit           Quit PhotoAgent")
    print()

    try:
        agent = create_photo_agent()

    except Exception as exc:
        print(f"Failed to create PhotoAgent: {exc}")
        return

    # Central manager for the current search results.
    result_manager = PhotoResultManager()
    conversation = ConversationManager()

    while True:

        try:
            user_input = input("You > ").strip()

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        # Local commands never go through Gemini.
        if handle_local_command(
            user_input,
            result_manager,
            conversation,
        ):
            continue

        # Natural-language requests go to Gemini.
        try:

            conversation.add_user_message(user_input)

            response = invoke_agent(agent, conversation)
            extracted_results = extract_photo_results(response)

            # The result manager always represents the latest search,
            # including an empty search.
            result_manager.set_results(extracted_results)

            answer = extract_text(response)

            conversation.add_assistant_message(answer)

            print()
            print("PhotoAgent >")
            print(answer)

            if extracted_results:
                print_photo_list(
                    result_manager.get_results()
                )

        except Exception as exc:

            print()
            print(f"PhotoAgent error: {exc}")
            print()


if __name__ == "__main__":
    main()