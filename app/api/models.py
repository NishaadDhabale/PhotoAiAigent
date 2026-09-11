from typing import Optional

from pydantic import BaseModel, Field


class PhotoResponse(BaseModel):
    id: int
    filename: str
    path: str
    date_taken: Optional[str] = None
    camera: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None
    similarity: Optional[float] = None


class PhotoListResponse(BaseModel):
    count: int
    results: list[PhotoResponse]


class SearchRequest(BaseModel):
    query: Optional[str] = None
    person: Optional[str] = None
    year: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    camera: Optional[str] = None
    filename: Optional[str] = None
    n_results: int = Field(default=10, ge=1, le=100)


class HealthResponse(BaseModel):
    status: str
    service: str