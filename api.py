import os
import uuid
from typing import Union
from fastapi import Depends, APIRouter, UploadFile, Request, Form
from starlette import status
from starlette.responses import JSONResponse, RedirectResponse

import botofunctions
import cloudfunctions
import crud
import login
from database import get_db
import schemas
from sqlalchemy.orm import Session
from login import get_current_user

router_api = APIRouter(prefix="/api")


@router_api.get("/get_video_s3/{video_name}")
async def get_video_s3(video_name:str):
    return RedirectResponse(botofunctions.create_presigned_url(video_name))



@router_api.post("/upload_video")
async def upload_video(request:Request,video: Union[UploadFile, None] = None, image:Union[UploadFile,None] = None, name: str = Form(), db: Session = Depends(get_db)):
    try:
        user = login.get_current_user(request)
        user = crud.get_user_by_id(db, user.id)
    except Exception:
        return RedirectResponse("/login_access", status_code=status.HTTP_303_SEE_OTHER)
    try:
        id = uuid.uuid4()
        video_temp = video.file.read()
        video_id_name = str(id) + ''.join(list(video.filename)[-4:])
        with open(video_id_name, 'wb') as f:
            f.write(video_temp)
        image_temp = image.file.read()
        image_id_name = str(id) + "img" + ''.join(list(image.filename)[-4:])
        with open(image_id_name, 'wb') as i:
            i.write(image_temp)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        video.file.close()
        image.file.close()
    cloudfunctions.put_file_to_server(video_id_name)
    cloudfunctions.put_file_to_server(image_id_name)
    uploaded_video = schemas.Video(id = id,
                                   name=name,
                                   video_path=video_id_name,
                                   image_path=botofunctions.create_presigned_url(image_id_name),
                                   user=user.username)
    crud.create_video(db=db,video=uploaded_video)
    os.remove(video_id_name)
    os.remove(image_id_name)
    return RedirectResponse(f"../user/{user.id}", status_code=status.HTTP_303_SEE_OTHER)
