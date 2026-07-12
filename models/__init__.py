from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from database import Base

class RoleModel(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)

    users = relationship("UserModel", back_populates="role")


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(20), primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    role = relationship("RoleModel", back_populates="users")
    creator_profile = relationship("CreatorProfileModel", back_populates="user", uselist=False, cascade="all, delete-orphan")
    agency_profile = relationship("AgencyProfileModel", back_populates="user", uselist=False, cascade="all, delete-orphan")
    account_settings = relationship("AccountSettingsModel", back_populates="user", uselist=False, cascade="all, delete-orphan")


class CreatorProfileModel(Base):
    __tablename__ = "creator_profiles"

    id = Column(String(20), primary_key=True, index=True)
    user_id = Column(String(20), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    username = Column(String(100))
    bio = Column(Text)
    youtube_url = Column(Text)
    instagram_url = Column(Text)
    facebook_url = Column(Text)
    linkedin_url = Column(Text)

    user = relationship("UserModel", back_populates="creator_profile")


class AgencyProfileModel(Base):
    __tablename__ = "agency_profiles"

    id = Column(String(20), primary_key=True, index=True)
    user_id = Column(String(20), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    agency_name = Column(String(150))
    website = Column(Text)
    contact_number = Column(String(20))

    user = relationship("UserModel", back_populates="agency_profile")


class AccountSettingsModel(Base):
    __tablename__ = "account_settings"

    id = Column(String(20), primary_key=True, index=True)
    user_id = Column(String(20), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    theme = Column(String(20), default="Light")
    notifications = Column(Boolean, default=True)
    language = Column(String(30), default="English")

    user = relationship("UserModel", back_populates="account_settings")


class AgencyCreatorModel(Base):
    __tablename__ = "agency_creators"

    id = Column(String(20), primary_key=True, index=True)
    agency_id = Column(String(20), ForeignKey("agency_profiles.id"), nullable=False)
    creator_id = Column(String(20), ForeignKey("creator_profiles.id"), nullable=False)
    assigned_on = Column(TIMESTAMP, server_default=func.current_timestamp())

    agency = relationship("AgencyProfileModel")
    creator = relationship("CreatorProfileModel")
