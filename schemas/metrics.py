from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema
        return core_schema.no_info_after_validator_function(cls, core_schema.str_schema())

class ContentMetricBase(BaseModel):
    postId: str
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    watchTime: int = 0
    reach: int = 0
    engagementRate: float = 0.0

class ContentMetricCreate(ContentMetricBase):
    pass

class ContentMetric(ContentMetricBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    snapshotDate: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class PerformanceTrendBase(BaseModel):
    creatorId: str
    trendDate: datetime
    totalViews: int = 0
    totalLikes: int = 0
    totalComments: int = 0
    totalShares: int = 0
    totalReach: int = 0
    averageWatchTime: float = 0.0
    engagementRate: float = 0.0

class PerformanceTrend(PerformanceTrendBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class ContentInsightBase(BaseModel):
    postId: str
    performanceScore: float = 0.0
    viralScore: float = 0.0
    rank: int = 0
    bestPostingTime: Optional[str] = None
    predictedGrowth: float = 0.0
    recommendation: Optional[str] = None

class ContentInsight(ContentInsightBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

# Schema for sync endpoint
class MetricSyncRequest(BaseModel):
    postId: str
    platform: str
    metrics: dict
