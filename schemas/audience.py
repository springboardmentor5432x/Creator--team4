from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema
        return core_schema.no_info_after_validator_function(
            cls,
            core_schema.str_schema()
        )


# =====================================================
# Audience Analytics
# =====================================================

class AudienceAnalyticsBase(BaseModel):
    creatorId: str
    totalFollowers: int = 0
    newFollowers: int = 0
    lostFollowers: int = 0
    growthRate: float = 0.0


class AudienceAnalytics(AudienceAnalyticsBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    recordedAt: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


# =====================================================
# Audience Demographics
# =====================================================

class AudienceDemographicsBase(BaseModel):
    creatorId: str
    ageGroup: dict = {}
    gender: dict = {}
    countries: dict = {}
    cities: dict = {}


class AudienceDemographics(AudienceDemographicsBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    recordedAt: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


# =====================================================
# Audience Behavior
# =====================================================

class AudienceBehaviorBase(BaseModel):
    creatorId: str
    activeHours: dict = {}
    activeDays: dict = {}
    averageWatchTime: float = 0.0
    returningViewers: int = 0


class AudienceBehavior(AudienceBehaviorBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    recordedAt: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


# =====================================================
# Request Schemas (POST APIs)
# =====================================================

class AudienceAnalyticsCreate(BaseModel):
    creatorId: str
    totalFollowers: int
    newFollowers: int
    lostFollowers: int
    growthRate: float


class AudienceDemographicsCreate(BaseModel):
    creatorId: str
    ageGroup: dict
    gender: dict
    countries: dict
    cities: dict


class AudienceBehaviorCreate(BaseModel):
    creatorId: str
    activeHours: dict
    activeDays: dict
    averageWatchTime: float
    returningViewers: int