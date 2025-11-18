# Build the server
FROM python:3.13-slim

COPY . /app

RUN pip3 install -r /app/requirements.txt

ENTRYPOINT ["python", "/app/server.py"]