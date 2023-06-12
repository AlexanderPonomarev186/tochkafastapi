FROM python:3.8.7
COPY requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "main.py"]
