import logging
from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from pydantic import ValidationError

from db.cache import Cache, get_cache_service
from db.elastic import get_elastic
from models.model import Genre
from services.search.base import AbstractSearchService
from services.search.elastic import ElasticSearchService
from services.service import Service
from utils.params import CommonQueryParams

logger = logging.getLogger()


class GenreService(Service):
    def __init__(self, cache: Cache, search_service: AbstractSearchService):
        super().__init__(cache, search_service, entity_name="genres", model=Genre)

    async def get_by_id(self, genre_id: str) -> Genre | None:
        """Получить жанр по id"""
        genre = await self._get_from_cache(genre_id)
        if genre:
            return genre
        try:
            genre_dict = await self.search_service.get_by_id(id=genre_id)
            if genre_dict:
                genre = Genre(**genre_dict)
                await self._put_to_cache(genre)
                return genre
        except ValidationError:
            logging.error(f"Error while validating {genre_dict}")

    async def get_list(self, params: CommonQueryParams) -> list[Genre]:
        """Получить список жанров"""
        raw_genres = await self.search_service.get_list(params=params)
        genres = [Genre(**raw_genre) for raw_genre in raw_genres]
        return genres


@lru_cache()
def get_genre_service(
    cache: Cache = Depends(get_cache_service), elastic: AsyncElasticsearch = Depends(get_elastic)
) -> GenreService:
    return GenreService(cache, search_service=ElasticSearchService(elastic, index="genres"))
