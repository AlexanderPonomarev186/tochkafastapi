import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request, Form
from pathlib import Path
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import uuid

from starlette import status
from starlette.responses import RedirectResponse

import crud
import login
import models
from database import engine, get_db
from login import router_jwt
from api import router_api

models.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

app.include_router(router_jwt)
app.include_router(router_api)


app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
)
templates = Jinja2Templates(directory="templates")
files = {
    item: os.path.join('samples_directory', item)
    for item in os.listdir('samples_directory')
}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)


# Dependency


# @app.get("/users/{user_id}")
# async def read_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


# @app.get("/users_by_email/{user_email}")
# async def read_user_by_email(user_email: str, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, email=user_email)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


# @app.get("/well_done")
# async def well_done(user: schemas.User = Depends(get_current_user)):
#     return "Well done " + user.email


@app.get('/')
async def mainPage(request:Request,db: Session = Depends(get_db)):
    list_of_videos = crud.get_videos(db)
    return templates.TemplateResponse("index.html", {'request':request, "videos":list_of_videos})

@app.post('/find')
async def findVideos(request:Request, db: Session = Depends(get_db), query: str = Form(None)):
    if query is None:
        return templates.TemplateResponse("none.html",{"request":request})
    list_of_videos = crud.get_videos_by_name(db, query)
    return templates.TemplateResponse("index.html", {'request':request, "videos":list_of_videos})

@app.get('/play_video/')
async def play_video(video_name: str, request: Request):
   return templates.TemplateResponse(
       'play_html5.html', {'request': request, 'video': {'name': video_name}})
    # else:
    #     return Response(status_code=404)

@app.get("/login_access")
async def login_on_site(request:Request, db: Session = Depends(get_db)):
    try:
        user = login.get_current_user(request)
        user = crud.get_user_by_id(db,user.id)
        return RedirectResponse(f"../user/{user.id}", status_code=status.HTTP_303_SEE_OTHER)
    except:
        return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signin")
async def signin(request:Request):
    return templates.TemplateResponse("signin.html", {"request": request})

@app.post("/user/{user_id}")
async def user_page(request:Request,db: Session = Depends(get_db)):
    try:
        user = login.get_current_user(request)
        # if request.cookies.get("User_id") != str(user_id):
        #     raise HTTPException(
        # status_code=status.HTTP_401_UNAUTHORIZED,
        # detail="Could not validate credentials",
        # headers={"WWW-Authenticate": "Bearer"},
        # )
        user = crud.get_user_by_id(db,user.id)
        return templates.TemplateResponse("user.html",{"request":request, "user":{"user_id": user.id, "user_login":user.email, "username": user.username}})
    except:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/user/{user_id}")
async def user_page(request:Request, db: Session = Depends(get_db)):
    try:
        user = login.get_current_user(request)
        # if request.cookies.get("User_id") != str(user_id):
        #     raise HTTPException(
        # status_code=status.HTTP_401_UNAUTHORIZED,
        # detail="Could not validate credentials",
        # headers={"WWW-Authenticate": "Bearer"},
        # )
        user = crud.get_user_by_id(db,user.id)
        return templates.TemplateResponse("user.html",{"request":request, "user":{"user_id": user.id, "user_login":user.email, "username": user.username}})
    except:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
        )


