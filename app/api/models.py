from typing import Optional,List
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


class PersonResponse(BaseModel):
    group_id: int
    name: str
    photo_count: int
    face_count: int
    representative_photo_id: int | None = None
    representative_image_url: str | None = None


class PeopleListResponse(BaseModel):
    count: int
    results: list[PersonResponse]

class TimelineMonthResponse(BaseModel):
    month: int
    month_name: str
    count: int
    results: list[PhotoResponse]


class TimelineYearResponse(BaseModel):
    year: int
    count: int
    months: list[TimelineMonthResponse]


class TimelineResponse(BaseModel):
    count: int
    total_photos: int
    dated_photos: int
    undated_photos: int
    years: list[TimelineYearResponse]
    undated: list[PhotoResponse]

class PersonPhotoResponse(BaseModel):
    id: int
    filename: str
    path: str
    date_taken: str | None = None
    camera: str | None = None
    location_name: str | None = None


class PersonPhotosResponse(BaseModel):
    group_id: int
    name: str
    count: int
    results: list[PersonPhotoResponse]


class PlaceResponse(BaseModel):
    location_name: str
    photo_count: int
    representative_photo_id: int | None = None
    representative_image_url: str | None = None


class PlacesListResponse(BaseModel):
    count: int
    total_photos: int
    located_photos: int
    unknown_photos: int
    results: list[PlaceResponse]


class PlacePhotoResponse(BaseModel):
    id: int
    filename: str
    path: str
    date_taken: str | None = None
    camera: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    location_name: str | None = None


class PlacePhotosResponse(BaseModel):
    location_name: str
    count: int
    results: list[PlacePhotoResponse]


class AgentMessage(BaseModel):
    role: str
    content: str


class AgentChatRequest(BaseModel):
    message: str
    history: list[AgentMessage] = []


class AgentPhotoResult(BaseModel):
    id: int
    filename: str
    path: str
    date_taken: str | None = None
    camera: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    location_name: str | None = None
    similarity: float | None = None


class AgentChatResponse(BaseModel):
    answer: str
    results: list[AgentPhotoResult] = []



class DuplicatePhotoResponse(BaseModel):
    id: int
    filename: str
    path: str
    date_taken: str | None = None
    camera: str | None = None
    location_name: str | None = None


class ExactDuplicateGroupResponse(BaseModel):
    group_id: int
    count: int
    photos: list[DuplicatePhotoResponse]


class NearDuplicateResponse(BaseModel):
    photo_a: DuplicatePhotoResponse
    photo_b: DuplicatePhotoResponse
    similarity: float


class DuplicateResponse(BaseModel):
    total_photos: int
    exact_group_count: int
    exact_duplicate_photo_count: int
    near_duplicate_count: int
    threshold: float
    exact_groups: list[ExactDuplicateGroupResponse]
    near_duplicates: list[NearDuplicateResponse]


class OrganizationPlanItem(BaseModel):
    photo_id: int
    filename: str
    source: str
    destination: str
    year: str
    status: str


class OrganizationSummary(BaseModel):
    photos: int
    safe: int
    conflicts: int
    already_organized: int
    missing_source: int


class OrganizationPreviewResponse(BaseModel):
    summary: OrganizationSummary
    plan: List[OrganizationPlanItem]


class OrganizationExecuteRequest(BaseModel):
    confirm: bool = False


class OrganizationResult(BaseModel):
    photo_id: int
    filename: str
    source: str
    destination: str
    status: str


class OrganizationExecuteResponse(BaseModel):
    count: int
    results: List[OrganizationResult]


class RenamePersonRequest(BaseModel):
    name: str


class RenamePersonResponse(BaseModel):
    id: int
    name: str


class MergePeopleRequest(BaseModel):
    group_ids: List[int]
    target_group_id: Optional[int] = None


class MergePeopleResponse(BaseModel):
    target_group_id: int
    merged_group_ids: List[int]
    count: int