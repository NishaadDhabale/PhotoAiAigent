from fastapi import APIRouter, HTTPException

from pathlib import Path

from fastapi.responses import FileResponse

from api.models import (
    HealthResponse,
    PhotoListResponse,
    PhotoResponse,
    SearchRequest,
)
from search_service import PhotoSearchService


router = APIRouter(prefix="/api")

search_service = PhotoSearchService()


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
def search(request: SearchRequest):
    try:
        has_filters = any(
            [
                request.person,
                request.year,
                request.start_date,
                request.end_date,
                request.location,
                request.camera,
                request.filename,
            ]
        )

        if request.query:
            if has_filters:
                results = search_service.hybrid_search(
                    semantic_query=request.query,
                    person=request.person,
                    year=request.year,
                    start_date=request.start_date,
                    end_date=request.end_date,
                    location=request.location,
                    camera=request.camera,
                    filename=request.filename,
                    n_results=request.n_results,
                )
            else:
                results = search_service.semantic_search(
                    query=request.query,
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
            )

        photos = [photo_response(photo) for photo in results]

        return {
            "count": len(photos),
            "results": photos,
        }

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))