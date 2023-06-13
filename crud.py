from sqlalchemy.orm import Session

import models
import schemas
import utils
import uuid


def get_user(db: Session, user_id: uuid.UUID):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db:Session, id: uuid.UUID):
    return db.query(models.User).filter(models.User.id == id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_videos(db:Session, skip: int = 0, limit: int = 100):
    return db.query(models.Video).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password, salt = utils.hash_password(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, salt=salt, id=uuid.uuid4())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_video(db:Session, video: schemas.Video) -> models.Video:
    db_video = models.Video(id=video.id, image=video.image_path, video=video.video_path)
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video