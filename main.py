import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request
from pathlib import Path
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import uuid

from starlette import status

import crud
import models
import schemas
import fastapi_jsonrpc as jsonrpc
from database import engine, get_db
from login import get_current_user, router_jwt
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
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)


# Dependency


@app.get("/users/{user_id}")
async def read_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/users_by_email/{user_email}")
async def read_user_by_email(user_email: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user_email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/well_done")
async def well_done(user: schemas.User = Depends(get_current_user)):
    return "Well done " + user.email




@app.get('/play_video/{video_name}')
async def play_video(video_name: str, request: Request):
    # video_path = files.get(video_name)
    # if video_path:
        return templates.TemplateResponse(
            'play_html5.html', {'request': request, 'video': {'name': video_name}})
    # else:
    #     return Response(status_code=404)

@app.get("/login_access")
async def login_on_site(request:Request):
    try:
        id = uuid.UUID(request.cookies.get("User_id"))
        user = crud.get_user_by_id(next(get_db()),id)
        return templates.TemplateResponse("user.html",{"request":request, "user":{"user_id": user.id, "user_login":user.email}})
    except:
        return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signin")
async def signin(request:Request):
    return templates.TemplateResponse("Signin.html", {"request": request})

@app.post("/user/{user_id}")
async def user_page(request:Request, user_id:uuid.UUID, db: Session = Depends(get_db)):
    try:
        if request.cookies.get("User_id") != str(user_id):
            raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
        )
        user = crud.get_user_by_id(db,user_id)
        return templates.TemplateResponse("user.html",{"request":request, "user":{"user_id": user.id, "user_login":user.email}})
    except:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
        )



