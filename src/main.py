import logging
from contextlib import asynccontextmanager

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1 import films, genres, persons
from core.config import settings
from core.logger import LOGGING
from db import elastic, cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    # при старте сервера
    cache.cache = Redis(host=settings.redis.host, port=settings.redis.port)
    elastic.es = AsyncElasticsearch(hosts=[f"{settings.es.scheme}://{settings.es.host}:{settings.es.port}"])
    yield
    # при выключении сервера
    await cache.cache.close()
    await elastic.es.close()


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=settings.app_port,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True,
    )
