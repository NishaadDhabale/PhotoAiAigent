from datetime import timedelta

from timeline import build_timeline, PHOTO_FOLDER


SESSION_GAP_MINUTES = 30


def build_sessions(timeline, gap_minutes=SESSION_GAP_MINUTES):
    """Group dated photos into chronological sessions."""

    sessions = []
    undated_photos = []

    current_session = []

    maximum_gap = timedelta(minutes=gap_minutes)

    for photo in timeline:

        # Keep undated photos instead of silently discarding them.
        if photo["date_taken"] is None:
            undated_photos.append(photo)
            continue

        if not current_session:
            current_session.append(photo)
            continue

        previous_photo = current_session[-1]

        time_difference = (
            photo["date_taken"]
            - previous_photo["date_taken"]
        )

        if time_difference <= maximum_gap:
            current_session.append(photo)

        else:
            sessions.append(current_session)
            current_session = [photo]

    # Save the final session.
    if current_session:
        sessions.append(current_session)

    return sessions, undated_photos


def describe_session(session):
    """Return useful information about a photo session."""

    if not session:
        return None

    start_time = session[0]["date_taken"]
    end_time = session[-1]["date_taken"]

    duration = end_time - start_time

    return {
        "photo_count": len(session),
        "start_time": start_time,
        "end_time": end_time,
        "duration": duration
    }


if __name__ == "__main__":

    timeline = build_timeline(PHOTO_FOLDER)

    sessions, undated_photos = build_sessions(timeline)

    print(f"Found {len(sessions)} sessions\n")

    for number, session in enumerate(sessions, start=1):

        information = describe_session(session)

        print(f"Session {number}")
        print(f"  Photos: {information['photo_count']}")
        print(f"  Start: {information['start_time']}")
        print(f"  End: {information['end_time']}")
        print(f"  Duration: {information['duration']}")

        for photo in session:
            print(f"    {photo['filename']}")

        print()

    print("Undated photos")
    print(f"  Count: {len(undated_photos)}")

    for photo in undated_photos:
        print(f"  {photo['filename']}")