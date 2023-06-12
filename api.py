import os
from typing import Union
from fastapi import Depends, APIRouter, UploadFile
from starlette.responses import JSONResponse, RedirectResponse

import botofunctions
import cloudfunctions
import schemas
from login import get_current_user

router_api = APIRouter(prefix="/api")


@router_api.get("/get_video_s3/{video_name}")
async def get_video_s3(video_name:str):
    return RedirectResponse(botofunctions.create_presigned_url(video_name))



@router_api.post("/upload_video")
async def upload_video(file: Union[UploadFile, None] = None):
    try:
        contents = file.file.read()
        with open(file.filename, 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()
    cloudfunctions.put_file_to_server(file.filename)
    os.remove(file.filename)
    return {"response": True}