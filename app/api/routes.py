from fastapi import APIRouter, HTTPException
from pathlib import Path
from duplicate_service import DuplicateService
from agent.agent import create_photo_agent
from fastapi.responses import FileResponse
from agent.result_normalizer import normalize_photo_results
from agent.result_pipeline import extract_photo_results
from organization_service import (
    get_organization_preview,
    execute_organization,
)
from photo_access import open_photo_location
from people_management import (
    rename_person,
    merge_person_groups,
)
from api.models import (
    HealthResponse,
    PhotoListResponse,
    PhotoResponse,
    SearchRequest,
    PersonResponse,
    PeopleListResponse,
    PersonPhotoResponse,
    PersonPhotosResponse,
    TimelineMonthResponse,
    TimelineYearResponse,
    TimelineResponse,
    PlaceResponse,
    PlacesListResponse,
    PlacePhotoResponse,
    PlacePhotosResponse,
    AgentChatRequest,
    AgentChatResponse,
    DuplicatePhotoResponse,
    ExactDuplicateGroupResponse,
    NearDuplicateResponse,
    DuplicateResponse,
    OrganizationPreviewResponse,
    OrganizationExecuteRequest,
    OrganizationExecuteResponse,
    RenamePersonRequest,
RenamePersonResponse,
MergePeopleRequest,
MergePeopleResponse,
)

from collections import defaultdict
from database import get_connection
from search_service import PhotoSearchService
from search_router import SearchRouter

router = APIRouter(prefix="/api")

search_service = PhotoSearchService()
search_router = SearchRouter(search_service)
duplicate_service = DuplicateService()


def photo_response(photo: dict) -> PhotoResponse:
    """Convert internal search result format to API response format."""
    data = dict(photo)

    if "id" not in data and "photo_id" in data:
        data["id"] = data.pop("photo_id")

    return PhotoResponse(**data)


@router.get("/health", response_model=HealthResponse)
def health():
    return {
        "status": "ok",
        "service": "PhotoAgent API",
    }


@router.get("/photos", response_model=PhotoListResponse)
def get_photos():
    try:
        results = search_service.structured_search()
        photos = [photo_response(photo) for photo in results]

        return {
            "count": len(photos),
            "results": photos,
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/photos/{photo_id}", response_model=PhotoResponse)
def get_photo(photo_id: int):
    try:
        results = search_service.structured_search()

        for photo in results:
            if int(photo["photo_id"]) == photo_id:
                return photo_response(photo)

        raise HTTPException(
            status_code=404,
            detail=f"Photo {photo_id} not found.",
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/photos/{photo_id}/image")
def get_photo_image(photo_id: int):
    try:
        results = search_service.structured_search()

        for photo in results:
            if int(photo["photo_id"]) == photo_id:
                image_path = Path(photo["path"])

                if not image_path.is_file():
                    raise HTTPException(
                        status_code=404,
                        detail="Photo file not found on disk.",
                    )

                return FileResponse(
                    path=image_path,
                    filename=image_path.name,
                )

        raise HTTPException(
            status_code=404,
            detail=f"Photo {photo_id} not found.",
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/search", response_model=PhotoListResponse)
def search_photos(request: SearchRequest):
    query = (request.query or "").strip()

    if query:
        results = search_router.search(
            query=query,
            n_results=request.n_results,
        )
    else:
        results = search_service.structured_search(
            person=request.person,
            year=request.year,
            start_date=request.start_date,
            end_date=request.end_date,
            location=request.location,
            camera=request.camera,
            filename=request.filename,
        )[:request.n_results]

    photos = [photo_response(photo) for photo in results]

    return {
        "count": len(photos),
        "results": photos,
    }



@router.get("/people", response_model=PeopleListResponse)
def get_people():
    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                f.person_group_id AS group_id,
                p.name AS person_name,
                COUNT(*) AS face_count,
                COUNT(DISTINCT f.photo_id) AS photo_count
            FROM faces f
            LEFT JOIN people p
                ON p.person_group_id = f.person_group_id
            WHERE f.person_group_id IS NOT NULL
            GROUP BY f.person_group_id
            ORDER BY
                CASE WHEN p.name IS NOT NULL THEN 0 ELSE 1 END,
                COALESCE(p.name, ''),
                f.person_group_id
            """
        ).fetchall()

        results = []

        for row in rows:
            # SQLite connection returns tuples:
            # (group_id, person_name, face_count, photo_count)
            group_id = int(row[0])
            person_name = row[1]
            face_count = int(row[2])
            photo_count = int(row[3])

            representative = conn.execute(
                """
                SELECT f.photo_id, f.confidence
                FROM faces f
                WHERE f.person_group_id = ?
                ORDER BY f.confidence DESC, f.photo_id ASC
                LIMIT 1
                """,
                (group_id,),
            ).fetchone()

            representative_photo_id = (
                int(representative[0])
                if representative
                else None
            )

            results.append(
                PersonResponse(
                    group_id=group_id,
                    name=person_name or f"Person {group_id}",
                    photo_count=photo_count,
                    face_count=face_count,
                    representative_photo_id=representative_photo_id,
                    representative_image_url=(
                        f"/api/people/{group_id}/thumbnail"
                        if representative_photo_id is not None
                        else None
                    ),
                )
            )

        return {
            "count": len(results),
            "results": results,
        }

    finally:
        conn.close()


@router.get(
    "/people/{group_id}/photos",
    response_model=PersonPhotosResponse,
)
def get_person_photos(group_id: int):
    conn = get_connection()

    try:
        person = conn.execute(
            """
            SELECT name
            FROM people
            WHERE person_group_id = ?
            LIMIT 1
            """,
            (group_id,),
        ).fetchone()

        name = (
            person[0]
            if person and person[0]
            else f"Person {group_id}"
        )

        rows = conn.execute(
            """
            SELECT DISTINCT
                ph.id,
                ph.filename,
                ph.path,
                ph.date_taken,
                ph.camera,
                ph.location_name
            FROM faces f
            JOIN photos ph
                ON ph.id = f.photo_id
            WHERE f.person_group_id = ?
            ORDER BY
                CASE WHEN ph.date_taken IS NULL THEN 1 ELSE 0 END,
                ph.date_taken DESC,
                ph.id DESC
            """,
            (group_id,),
        ).fetchall()

        results = [
            PersonPhotoResponse(
                id=int(row[0]),
                filename=row[1],
                path=row[2],
                date_taken=row[3],
                camera=row[4],
                location_name=row[5],
            )
            for row in rows
        ]

        return {
            "group_id": group_id,
            "name": name,
            "count": len(results),
            "results": results,
        }

    finally:
        conn.close()


@router.get("/people/{group_id}/thumbnail")
def get_person_thumbnail(group_id: int):
    from io import BytesIO

    from PIL import Image
    from fastapi.responses import StreamingResponse

    conn = get_connection()

    try:
        row = conn.execute(
            """
            SELECT
                f.x,
                f.y,
                f.width,
                f.height,
                ph.path
            FROM faces f
            JOIN photos ph
                ON ph.id = f.photo_id
            WHERE f.person_group_id = ?
            ORDER BY
                f.confidence DESC,
                f.photo_id ASC
            LIMIT 1
            """,
            (group_id,),
        ).fetchone()

    finally:
        conn.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Person group {group_id} not found.",
        )

    # SQLite tuple:
    # (x, y, width, height, path)
    x = row[0]
    y = row[1]
    width = row[2]
    height = row[3]
    image_path = Path(row[4])

    if not image_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Photo file not found on disk.",
        )

    try:
        image = Image.open(image_path).convert("RGB")

        image_width, image_height = image.size

        x = max(0, int(x))
        y = max(0, int(y))
        width = max(1, int(width))
        height = max(1, int(height))

        padding_x = int(width * 0.45)
        padding_y = int(height * 0.55)

        left = max(0, x - padding_x)
        top = max(0, y - padding_y)
        right = min(
            image_width,
            x + width + padding_x,
        )
        bottom = min(
            image_height,
            y + height + padding_y,
        )

        crop = image.crop(
            (left, top, right, bottom)
        )

        crop_width, crop_height = crop.size
        square_size = max(crop_width, crop_height)

        square = Image.new(
            "RGB",
            (square_size, square_size),
            "white",
        )

        paste_x = (square_size - crop_width) // 2
        paste_y = (square_size - crop_height) // 2

        square.paste(crop, (paste_x, paste_y))

        output = BytesIO()

        square.save(
            output,
            format="JPEG",
            quality=90,
        )

        output.seek(0)

        return StreamingResponse(
            output,
            media_type="image/jpeg",
            headers={
                "Cache-Control": "public, max-age=3600",
            },
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate person thumbnail: {exc}",
        )



@router.get("/timeline", response_model=TimelineResponse)
def get_timeline():
    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                id,
                filename,
                path,
                date_taken,
                camera,
                latitude,
                longitude,
                location_name
            FROM photos
            ORDER BY
                CASE
                    WHEN date_taken IS NULL THEN 1
                    ELSE 0
                END,
                date_taken DESC,
                id DESC
            """
        ).fetchall()

    finally:
        conn.close()

    years = defaultdict(lambda: defaultdict(list))
    undated = []

    for row in rows:
        photo = PhotoResponse(
            id=int(row[0]),
            filename=row[1],
            path=row[2],
            date_taken=row[3],
            camera=row[4],
            latitude=row[5],
            longitude=row[6],
            location_name=row[7],
        )

        if not row[3]:
            undated.append(photo)
            continue

        date_string = row[3]

        try:
            year = int(date_string[:4])
            month = int(date_string[5:7])
        except (ValueError, IndexError):
            undated.append(photo)
            continue

        if month < 1 or month > 12:
            undated.append(photo)
            continue

        years[year][month].append(photo)

    month_names = [
        "",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    year_results = []

    for year in sorted(years.keys(), reverse=True):
        month_results = []

        for month in sorted(years[year].keys(), reverse=True):
            photos = years[year][month]

            month_results.append(
                TimelineMonthResponse(
                    month=month,
                    month_name=month_names[month],
                    count=len(photos),
                    results=photos,
                )
            )

        year_count = sum(
            month.count for month in month_results
        )

        year_results.append(
            TimelineYearResponse(
                year=year,
                count=year_count,
                months=month_results,
            )
        )

    dated_count = sum(
        year.count for year in year_results
    )

    return TimelineResponse(
        count=len(year_results),
        total_photos=len(rows),
        dated_photos=dated_count,
        undated_photos=len(undated),
        years=year_results,
        undated=undated,
    )




@router.get("/places", response_model=PlacesListResponse)
def get_places():
    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                location_name,
                COUNT(*) AS photo_count
            FROM photos
            WHERE location_name IS NOT NULL
              AND TRIM(location_name) != ''
            GROUP BY location_name
            ORDER BY photo_count DESC, location_name ASC
            """
        ).fetchall()

        total_row = conn.execute(
            """
            SELECT
                COUNT(*) AS total_photos,
                SUM(
                    CASE
                        WHEN location_name IS NOT NULL
                         AND TRIM(location_name) != ''
                        THEN 1
                        ELSE 0
                    END
                ) AS located_photos
            FROM photos
            """
        ).fetchone()

        total_photos = int(total_row[0] or 0)
        located_photos = int(total_row[1] or 0)
        unknown_photos = total_photos - located_photos

        results = []

        for row in rows:
            location_name = row[0]
            photo_count = int(row[1])

            representative = conn.execute(
                """
                SELECT
                    id
                FROM photos
                WHERE location_name = ?
                ORDER BY
                    CASE
                        WHEN date_taken IS NULL THEN 1
                        ELSE 0
                    END,
                    date_taken DESC,
                    id DESC
                LIMIT 1
                """,
                (location_name,),
            ).fetchone()

            representative_photo_id = (
                int(representative[0])
                if representative
                else None
            )

            results.append(
                PlaceResponse(
                    location_name=location_name,
                    photo_count=photo_count,
                    representative_photo_id=representative_photo_id,
                    representative_image_url=(
                        f"/api/photos/{representative_photo_id}/image"
                        if representative_photo_id is not None
                        else None
                    ),
                )
            )

        return PlacesListResponse(
            count=len(results),
            total_photos=total_photos,
            located_photos=located_photos,
            unknown_photos=unknown_photos,
            results=results,
        )

    finally:
        conn.close()


@router.get(
    "/places/unknown/photos",
    response_model=PlacePhotosResponse,
)
def get_unknown_place_photos():
    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                id,
                filename,
                path,
                date_taken,
                camera,
                latitude,
                longitude,
                location_name
            FROM photos
            WHERE location_name IS NULL
               OR TRIM(location_name) = ''
            ORDER BY
                CASE
                    WHEN date_taken IS NULL THEN 1
                    ELSE 0
                END,
                date_taken DESC,
                id DESC
            """
        ).fetchall()

        results = [
            PlacePhotoResponse(
                id=int(row[0]),
                filename=row[1],
                path=row[2],
                date_taken=row[3],
                camera=row[4],
                latitude=row[5],
                longitude=row[6],
                location_name=row[7],
            )
            for row in rows
        ]

        return PlacePhotosResponse(
            location_name="Unknown location",
            count=len(results),
            results=results,
        )

    finally:
        conn.close()





@router.get(
    "/places/{location_name}/photos",
    response_model=PlacePhotosResponse,
)
def get_place_photos(location_name: str):
    from urllib.parse import unquote

    location_name = unquote(location_name)

    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                id,
                filename,
                path,
                date_taken,
                camera,
                latitude,
                longitude,
                location_name
            FROM photos
            WHERE location_name = ?
            ORDER BY
                CASE
                    WHEN date_taken IS NULL THEN 1
                    ELSE 0
                END,
                date_taken DESC,
                id DESC
            """,
            (location_name,),
        ).fetchall()

        results = [
            PlacePhotoResponse(
                id=int(row[0]),
                filename=row[1],
                path=row[2],
                date_taken=row[3],
                camera=row[4],
                latitude=row[5],
                longitude=row[6],
                location_name=row[7],
            )
            for row in rows
        ]

        return PlacePhotosResponse(
            location_name=location_name,
            count=len(results),
            results=results,
        )

    finally:
        conn.close()


@router.post(
    "/agent/chat",
    response_model=AgentChatResponse,
)
def agent_chat(request: AgentChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    try:
        agent = create_photo_agent()

        messages = []

        for item in request.history:
            if item.role not in {"user", "assistant"}:
                continue

            messages.append(
                {
                    "role": item.role,
                    "content": item.content,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": message,
            }
        )

        response = agent.invoke(
            {
                "messages": messages,
            }
        )

        response_messages = response.get(
            "messages",
            [],
        )

        answer = ""

        for item in reversed(response_messages):
            if getattr(item, "type", None) != "ai":
                continue

            content = getattr(item, "content", None)

            # Normal string response
            if isinstance(content, str):
                if content.strip():
                    answer = content.strip()
                    break

            # Gemini/LangChain content-block response
            elif isinstance(content, list):
                text_parts = []

                for block in content:
                    if isinstance(block, dict):
                        text = block.get("text")
                        if text:
                            text_parts.append(str(text))

                    elif isinstance(block, str):
                        text_parts.append(block)

                if text_parts:
                    answer = "\n".join(text_parts).strip()
                    break

        if not answer:
            answer = "I couldn't generate a response."
        # -------------------------------------------------
        # Extract photo results produced by the agent tools
        # -------------------------------------------------

        normalized_results = extract_photo_results(
            response_messages
        )

        results = []

        for photo in normalized_results:
            results.append(
                {
                    "id": photo["id"],
                    "filename": photo.get(
                        "filename",
                        "",
                    ),
                    "path": photo.get(
                        "path",
                        "",
                    ),
                    "date_taken": photo.get(
                        "date_taken"
                    ),
                    "camera": photo.get(
                        "camera"
                    ),
                    "latitude": photo.get(
                        "latitude"
                    ),
                    "longitude": photo.get(
                        "longitude"
                    ),
                    "location_name": photo.get(
                        "location_name"
                    ),
                    "similarity": photo.get(
                        "similarity"
                    ),
                }
            )

        return AgentChatResponse(
            answer=answer,
            results=results,
        )

    except Exception as exc:
        error_text = str(exc)

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
            or "quota" in error_text.lower()
        ):
            raise HTTPException(
                status_code=429,
                detail=(
                    "Gemini API quota is currently "
                    "exhausted. The local PhotoAgent "
                    "data and search system are still "
                    "available."
                ),
            )

        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {error_text}",
        )



@router.get(
    "/duplicates",
    response_model=DuplicateResponse,
)
def get_duplicates():
    try:
        data = duplicate_service.find_duplicates()

        exact_groups = []

        exact_duplicate_photo_count = 0

        for group_id, group in enumerate(
            data["exact_groups"],
            start=1,
        ):
            photos = []

            for photo in group:
                photos.append(
                    DuplicatePhotoResponse(
                        id=int(photo["id"]),
                        filename=photo["filename"],
                        path=photo["path"],
                        date_taken=photo.get(
                            "date_taken"
                        ),
                        camera=photo.get(
                            "camera"
                        ),
                        location_name=photo.get(
                            "location_name"
                        ),
                    )
                )

            exact_duplicate_photo_count += len(
                photos
            )

            exact_groups.append(
                ExactDuplicateGroupResponse(
                    group_id=group_id,
                    count=len(photos),
                    photos=photos,
                )
            )

        near_duplicates = []

        for match in data["near_duplicates"]:
            first = match["photo_a"]
            second = match["photo_b"]

            near_duplicates.append(
                NearDuplicateResponse(
                    photo_a=DuplicatePhotoResponse(
                        id=int(first["id"]),
                        filename=first["filename"],
                        path=first["path"],
                        date_taken=first.get(
                            "date_taken"
                        ),
                        camera=first.get(
                            "camera"
                        ),
                        location_name=first.get(
                            "location_name"
                        ),
                    ),
                    photo_b=DuplicatePhotoResponse(
                        id=int(second["id"]),
                        filename=second["filename"],
                        path=second["path"],
                        date_taken=second.get(
                            "date_taken"
                        ),
                        camera=second.get(
                            "camera"
                        ),
                        location_name=second.get(
                            "location_name"
                        ),
                    ),
                    similarity=float(
                        match["similarity"]
                    ),
                )
            )

        return DuplicateResponse(
            total_photos=data["total_photos"],
            exact_group_count=len(
                exact_groups
            ),
            exact_duplicate_photo_count=(
                exact_duplicate_photo_count
            ),
            near_duplicate_count=len(
                near_duplicates
            ),
            threshold=data["threshold"],
            exact_groups=exact_groups,
            near_duplicates=near_duplicates,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Duplicate detection failed: {exc}",
        )


@router.get(
    "/organization/preview",
    response_model=OrganizationPreviewResponse,
)
def organization_preview():
    """
    Generate a read-only organization preview.

    This endpoint NEVER modifies files.
    """

    try:

        return get_organization_preview()

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.post(
    "/organization/execute",
    response_model=OrganizationExecuteResponse,
)
def organization_execute(
    request: OrganizationExecuteRequest,
):
    """
    Execute photo organization.

    Explicit confirmation is required.
    """

    if not request.confirm:

        raise HTTPException(
            status_code=400,
            detail=(
                "Organization requires explicit confirmation. "
                "Set confirm=true."
            ),
        )

    try:

        return execute_organization(
            confirm=True,
        )

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    except FileExistsError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    except PermissionError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.patch(
    "/people/{person_id}",
    response_model=RenamePersonResponse,
)
def rename_person_route(
    person_id: int,
    request: RenamePersonRequest,
):
    try:
        return rename_person(person_id, request.name)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.post(
    "/people/merge",
    response_model=MergePeopleResponse,
)
def merge_people_route(
    request: MergePeopleRequest,
):
    try:
        return merge_person_groups(
            request.group_ids,
            request.target_group_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.post("/photos/{photo_id}/open-location")
def open_photo_location_route(photo_id: int):
    """
    Open Windows Explorer and select the requested photo.
    """

    try:
        photo = open_photo_location(photo_id)

        return {
            "success": True,
            "photo_id": photo["id"],
            "filename": photo["filename"],
            "path": photo["path"],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )