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


# ---------------------------------------------------------------------------
# Revenue Analytics Module Exceptions
# ---------------------------------------------------------------------------

class RevenueBaseException(HTTPException):
    """Base exception for all revenue analytics errors."""

    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class InvalidRevenueDataException(RevenueBaseException):
    """Raised when negative revenue or invalid payload values are passed."""

    def __init__(self, detail: str = "Invalid revenue data provided."):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class DuplicateSponsorshipException(RevenueBaseException):
    """Raised when a duplicate sponsorship campaign is created for the same creator and company."""

    def __init__(self, detail: str = "A sponsorship campaign with this name already exists for this creator."):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class InvalidDateRangeException(RevenueBaseException):
    """Raised when end_date < start_date or dates are invalid."""

    def __init__(self, detail: str = "End date cannot be earlier than start date."):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class RevenueNotFoundException(RevenueBaseException):
    """Raised when a revenue record is not found."""

    def __init__(self, entity: str = "Revenue record", record_id: str = ""):
        super().__init__(
            detail=f"{entity} with ID '{record_id}' not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UnauthorizedRevenueAccessException(RevenueBaseException):
    """Raised when a user attempts to access revenue records they do not own or manage."""

    def __init__(self, detail: str = "Not authorized to access revenue records for this creator."):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)

