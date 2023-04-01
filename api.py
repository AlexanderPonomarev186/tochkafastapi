from fastapi.responses import StreamingResponse, FileResponse
from fastapi.responses import Response
from fastapi import FastAPI, Request
import requests
import botofunctions


def get_video_api(video_name: str, files:dict, response_class=StreamingResponse):
    video_path = files.get(video_name)
    if video_path:
        return StreamingResponse(open(video_path, 'rb'))
    else:
        return Response(status_code=404)



def get_video_s3(video_name:str):
    return botofunctions.create_presigned_url('tochkateststorage', video_name)
    # if url is not None:
    #     response = requests.get(url)
