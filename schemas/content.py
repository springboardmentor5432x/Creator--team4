from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema
        return core_schema.no_info_after_validator_function(cls, core_schema.str_schema())

class SocialAccountBase(BaseModel):
    creatorId: str
    platform: str
    platformUserId: str
    accountName: str
    username: str
    profileUrl: Optional[str] = None
    profilePicture: Optional[str] = None
    followers: int = 0
    isActive: bool = True

class SocialAccountCreate(SocialAccountBase):
    accessToken: str
    refreshToken: str
    tokenExpiry: datetime

class SocialAccount(SocialAccountBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    connectedAt: datetime
    lastSynced: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class ContentPostBase(BaseModel):
    creatorId: str
    socialAccountId: str
    platform: str
    platformPostId: str
    title: str
    description: Optional[str] = None
    hashtags: List[str] = []
    contentType: str
    category: Optional[str] = None
    duration: Optional[int] = None
    language: Optional[str] = None
    contentUrl: Optional[str] = None
    thumbnailUrl: Optional[str] = None
    publishedAt: datetime
    visibility: str
    status: str

class ContentPostCreate(ContentPostBase):
    pass

class ContentPost(ContentPostBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    lastSync: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
