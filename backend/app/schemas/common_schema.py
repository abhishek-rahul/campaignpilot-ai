from datetime import datetime
from typing import Any, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseMeta(BaseModel):
    request_id: str
    timestamp: datetime | str


class ApiError(BaseModel):
    code: str
    details: list[dict[str, Any]] = Field(default_factory=list)


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T | None
    error: ApiError | None
    meta: ResponseMeta


class Pagination(BaseModel):
    page: int = 1
    page_size: int = 20
    total_items: int = 0
    total_pages: int = 0
