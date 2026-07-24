"""
utils/exceptions.py — Analytics Module Exception Classes

Custom exception hierarchy for the growth analytics module.
All classes inherit from FastAPI's HTTPException so they automatically
produce the correct HTTP status code and JSON error body.
"""

from fastapi import HTTPException, status


class AnalyticsBaseException(HTTPException):
    """Base exception for all analytics-related errors."""

    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class InsufficientDataError(AnalyticsBaseException):
    """
    Raised when there is not enough historical data for a calculation.
    E.g., prediction requires at least 7 days of data.
    """

    def __init__(self, detail: str = "Insufficient historical data. At least 7 days of data required."):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ContentNotFoundError(AnalyticsBaseException):
    """Raised when a content_id does not exist in the database."""

    def __init__(self, content_id: str):
        super().__init__(
            detail=f"Content with id '{content_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class HashtagNotFoundError(AnalyticsBaseException):
    """Raised when a hashtag name does not exist in the database."""

    def __init__(self, hashtag: str):
        super().__init__(
            detail=f"Hashtag '{hashtag}' not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class PredictionError(AnalyticsBaseException):
    """Raised when the prediction algorithm encounters an error."""

    def __init__(self, detail: str = "Prediction calculation failed."):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
