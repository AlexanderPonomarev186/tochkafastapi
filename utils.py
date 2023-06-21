import hashlib
import random
import string

from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

import crud
from fastapi import HTTPException

import models
import schemas

def get_random_string(length=12):
    """ Генерирует случайную строку, использующуюся как соль """
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def hash_password(password: str, salt: str = None):
    """ Хеширует пароль с солью """
    if salt is None:
        salt = get_random_string()
    enc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return enc.hex(), salt


def validate_password(password: str, hashed_password: str, salt: str) -> bool:
    hash_input, salt = hash_password(password, salt)
    return hash_input == hashed_password

def check_password(user: schemas.Login, db: Session):
    db_user = crud.get_user_by_email(db, email=user.login.lower())
    if db_user is None:
        return RedirectResponse("/signin")
    validate = validate_password(user.password, db_user.hashed_password, db_user.salt)
    if not validate:
        raise HTTPException(status_code=400, detail="Wrong password")
    return db_user
