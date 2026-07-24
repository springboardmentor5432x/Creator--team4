"""
schemas/pagination.py — Reusable Pagination Schemas

Provides PaginationParams for query parsing and PaginatedResponse[T] for
consistent paginated API responses across all analytics endpoints.
"""

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field
from math import ceil

T = TypeVar("T")


class PaginationParams(BaseModel):
    """
    Standard pagination + sorting query parameters.

    Usage in routes:
        @router.get("/items")
        async def list_items(params: PaginationParams = Depends()):
            ...
    """
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(default=None, description="Field name to sort by")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort direction")

    @property
    def skip(self) -> int:
        """MongoDB skip value."""
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response wrapper.

    Usage:
        PaginatedResponse[HashtagResponse](items=[...], total=100, page=1, page_size=20)
    """
    items: List[T]
    total: int = Field(description="Total number of items across all pages")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Items per page")
    total_pages: int = Field(description="Total number of pages")

    @classmethod
    def create(cls, items: List[T], total: int, page: int, page_size: int):
        """Factory method to auto-calculate total_pages."""
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=ceil(total / page_size) if page_size > 0 else 0,
        )
