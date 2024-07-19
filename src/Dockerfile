FROM python:3.11-slim

EXPOSE 8000

WORKDIR /opt/app

RUN groupadd -r web && useradd -r -g web web

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt
COPY requirements-prod.txt requirements-prod.txt

RUN  pip install --upgrade pip && pip install -r requirements.txt -r requirements-prod.txt

COPY ./src .

USER web
ENTRYPOINT ["gunicorn", "main:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker"]
