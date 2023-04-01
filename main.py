import os
from typing import Union

import uvicorn
import json
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import botofunctions
import crud
import models
import schemas
import api
import utils
import cloudfunctions
import fastapi_jsonrpc as jsonrpc
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()




app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
files = {
    item: os.path.join('samples_directory', item)
    for item in os.listdir('samples_directory')
}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)

origins = [
    "http://localhost",
    "http://localhost:5000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email.lower())
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

# @app.get("/users/", response_model=list[schemas.User])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = crud.get_users(db, skip=skip, limit=limit)
#     return users


@app.get("/users/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/users/check_password")
async def check_password(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email.lower())
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    validate = utils.validate_password(user.password, db_user.hashed_password, db_user.salt)
    if not validate:
        raise HTTPException(status_code=400, detail="Wrong password")
    return db_user


@app.get("/api/get_video/{video_name}")
async def get_video(video_name: str):
    return api.get_video_api(video_name, files)


@app.get("/api/get_video_s3/{video_name}")
async def get_video_s3(video_name:str):
    return RedirectResponse(botofunctions.create_presigned_url(video_name))


@app.get('/play_video/{video_name}')
async def play_video(video_name: str, request: Request, response_class=HTMLResponse):
    video_path = files.get(video_name)
    if video_path:
        return templates.TemplateResponse(
            'play_html5.html', {'request': request, 'video': {'path': video_path, 'name': video_name}})
    else:
        return Response(status_code=404)

@app.post("/api/upload_video")
async def upload_video(video:schemas.Video):
    cloudfunctions.put_file_to_server(video.video_path)
    return { "response":True}