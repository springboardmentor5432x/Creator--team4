from pydantic import BaseModel, Field
from typing import Optional, List, Dict
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
# Audience Analytics (Overview + Follower Growth)
# =====================================================

class AudienceAnalyticsBase(BaseModel):
    creatorId: str
    # Follower counts
    totalFollowers: int = 0
    newFollowers: int = 0
    lostFollowers: int = 0
    # Growth breakdown by period
    dailyGrowth: int = 0
    weeklyGrowth: int = 0
    monthlyGrowth: int = 0
    growthRate: float = 0.0          # percentage growth (period-agnostic)
    # Reach & Impressions
    reach: int = 0
    impressions: int = 0
    uniqueViewers: int = 0
    # Engagement
    averageEngagementRate: float = 0.0


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
    # Age distribution — key: age range string, value: percentage
    ageGroup: Dict[str, float] = {}
    # Gender distribution — key: gender label, value: percentage
    gender: Dict[str, float] = {}
    # Geographic distribution — key: country name, value: percentage
    countries: Dict[str, float] = {}
    # City-level breakdown — key: city name, value: percentage
    cities: Dict[str, float] = {}
    # Region/state breakdown — key: region name, value: percentage
    regions: Dict[str, float] = {}
    # Pre-computed ranked lists for quick display
    topCountries: List[str] = []
    topCities: List[str] = []


class AudienceDemographics(AudienceDemographicsBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    recordedAt: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


# =====================================================
# Audience Behavior (Activity + Device + Engagement)
# =====================================================

class AudienceBehaviorBase(BaseModel):
    creatorId: str
    # Activity patterns
    activeHours: Dict[str, float] = {}   # key: "0"–"23", value: relative activity %
    activeDays: Dict[str, float] = {}    # key: "Monday"–"Sunday", value: relative activity %
    peakEngagementTime: Optional[str] = None   # e.g. "Saturday 8PM"
    # Device usage breakdown (percentages)
    deviceUsage: Dict[str, float] = {}   # { "mobile": 72.5, "desktop": 20.0, "tablet": 5.0, "smartTV": 2.5 }
    mobileUsers: float = 0.0
    desktopUsers: float = 0.0
    tabletUsers: float = 0.0
    smartTVUsers: float = 0.0
    # Engagement metrics
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    engagementRate: float = 0.0
    # Viewer retention
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
    totalFollowers: int = 0
    newFollowers: int = 0
    lostFollowers: int = 0
    dailyGrowth: int = 0
    weeklyGrowth: int = 0
    monthlyGrowth: int = 0
    growthRate: float = 0.0
    reach: int = 0
    impressions: int = 0
    uniqueViewers: int = 0
    averageEngagementRate: float = 0.0


class AudienceDemographicsCreate(BaseModel):
    ageGroup: Dict[str, float] = {}
    gender: Dict[str, float] = {}
    countries: Dict[str, float] = {}
    cities: Dict[str, float] = {}
    regions: Dict[str, float] = {}
    topCountries: List[str] = []
    topCities: List[str] = []


class AudienceBehaviorCreate(BaseModel):
    activeHours: Dict[str, float] = {}
    activeDays: Dict[str, float] = {}
    peakEngagementTime: Optional[str] = None
    deviceUsage: Dict[str, float] = {}
    mobileUsers: float = 0.0
    desktopUsers: float = 0.0
    tabletUsers: float = 0.0
    smartTVUsers: float = 0.0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    engagementRate: float = 0.0
    averageWatchTime: float = 0.0
    returningViewers: int = 0