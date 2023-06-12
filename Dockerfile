FROM python:3.8.7
WORKDIR: /Test_fastapi_project/
COPY requirements.txt /Test_fastapi_project/
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
