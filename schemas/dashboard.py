from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from schemas.content import ContentPost

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema
        return core_schema.no_info_after_validator_function(cls, core_schema.str_schema())

class AnalyticsSummaryBase(BaseModel):
    creatorId: str
    totalViews: int = 0
    totalLikes: int = 0
    totalComments: int = 0
    totalShares: int = 0
    totalReach: int = 0
    averageEngagementRate: float = 0.0
    topContent: List[str] = []

class AnalyticsSummary(AnalyticsSummaryBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    lastUpdated: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class DashboardSummaryResponse(BaseModel):
    totalViews: int
    totalLikes: int
    averageEngagement: float
    bestContent: Optional[ContentPost] = None
    worstContent: Optional[ContentPost] = None
