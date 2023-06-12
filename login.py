from datetime import datetime, timedelta
from typing import Union
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from starlette.responses import JSONResponse, RedirectResponse
import crud
import schemas
from database import SessionLocal, get_db
import utils


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
router_jwt = APIRouter(prefix="/login")

def create_access_token(data: dict, expires_delta: Union[str, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def token(user):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )


@router_jwt.post("/signin_create_user")
async def create_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = schemas.UserCreate(**{"email": form_data.username, "password":form_data.password})
    db_user = crud.get_user_by_email(db, email=user.email.lower())
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db=db, user=user)
    access_token = token(user)
    response = RedirectResponse(f"../user/{user.id}")
    response.set_cookie(key="Authorization", value=access_token, secure=True, httponly=True)
    response.set_cookie(key="User_id", value=user.id, secure=True, httponly=True)
    return response

@router_jwt.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = utils.check_password(schemas.Login(login=form_data.username, password=form_data.password), db)
    access_token = token(user)
    response = RedirectResponse(f"../user/{user.id}")
    response.set_cookie(key="Authorization", value=access_token, secure=True, httponly=True)
    response.set_cookie(key="User_id", value=user.id, secure=True, httponly=True)
    return response

@router_jwt.post("/logout")
async def logout():
    response = JSONResponse({"status":"logout"})
    response.delete_cookie("Authorization")
    response.delete_cookie("User_id")
    return response



def get_current_user(request: Request):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = request.cookies.get("Authorization")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except (JWTError, AttributeError):
        raise credentials_exception
    session = SessionLocal()
    user = crud.get_user_by_email(session, email=token_data.email)
    session.close()
    if user is None:
        raise credentials_exception
    return user




