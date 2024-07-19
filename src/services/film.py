from functools import lru_cache

from fastapi import Depends

from db.cache import Cache, get_cache_service
from db.elastic import AsyncElasticsearch, get_elastic
from models.model import Film, Genre
from services.search.base import AbstractSearchService, NestedObjectQuery
from services.search.elastic import ElasticSearchService
from services.service import Service
from utils.params import CommonQueryParams

PERSON_ROLES = ("actor", "director", "writer")


class FilmService(Service):
    """Сервис для работы с кинопроизведениями"""

    def __init__(self, cache: Cache, search_service: AbstractSearchService):
        super().__init__(cache, search_service, entity_name="movies", model=Film)

    async def search(self, text: str, query_params: CommonQueryParams) -> list[Film]:
        """Метод для поиска фильмов по текстовым полям"""
        fields = ["title^3", "description", "actors_names", "writers_names", "directors_names"]
        raw_films = await self.search_service.text_search(
            params=query_params,
            search_query=text,
            search_fields=fields,
        )
        return [Film(**film) for film in raw_films]

    async def get_films(self, query_params: CommonQueryParams, genre: Genre | None = None) -> list[Film]:
        """Метод для получения списка фильмов с возможностью фильтрации по жанру"""
        search_query = genre.name if genre else None
        films_raw = await self.search_service.text_search(search_fields=["genres"], search_query=search_query, params=query_params)
        return [Film(**raw_film) for raw_film in films_raw]

    async def get_person_films(self, person_id: str, params: CommonQueryParams):
        nested_objects = [
            NestedObjectQuery(name=f"{role}s", filter_field="id", term_value=person_id) for role in PERSON_ROLES
        ]
        person_films = await self.search_service.get_list(
            params=params, nested_objects=nested_objects
        )
        return [Film(**raw_film) for raw_film in person_films]


@lru_cache()
def get_film_service(
    cache: Cache = Depends(get_cache_service),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(cache, search_service=ElasticSearchService(elastic, index="movies"))
