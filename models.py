from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UUID
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    username = Column(String, unique=True, index=True)
    id = Column(UUID, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    salt = Column(String)
    is_active = Column(Boolean, default=True)
    # role = Column(Integer, default=0)


class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID, primary_key=True, index=True)
    name = Column(String)
    image = Column(String, unique=True, index=True)
    video = Column(String, unique=True, index=True)
    user = Column(String, index=True)