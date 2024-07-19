import logging
from functools import lru_cache
from typing import cast

from fastapi import Depends
from pydantic import ValidationError

from db.cache import Cache, get_cache_service
from db.elastic import AsyncElasticsearch, get_elastic
from models.model import Film, Person, PersonFilm
from services.film import PERSON_ROLES, FilmService, get_film_service
from services.search.base import AbstractSearchService
from services.search.elastic import ElasticSearchService
from services.service import Service
from utils.params import CommonQueryParams

logger = logging.getLogger()


class PersonService(Service):
    def __init__(self, cache: Cache, search_service: AbstractSearchService, film_service: FilmService):
        super().__init__(cache, search_service, entity_name="persons", model=Person)
        self.film_service = film_service

    async def get_by_id(self, person_id: str) -> Person | None:
        person = cast(Person, await self._get_from_cache(person_id))
        if not person:
            person_dict = await self.search_service.get_by_id(id=person_id)
            if not person_dict:
                return None
            person = Person(**person_dict)
            related_filmworks = await self.film_service.get_person_films(
                # у нас нет отдельной пагинации фильмов внутри персоны, 
                # 10000 это ограничение метода поиска ES, по-умолчанию отдается только 10
                # предпологаем что персона не может участвовать при создании больше 10000 фильмов
                person.id, params=CommonQueryParams(page_size=10000)
            )
            try:
                person.films = self._get_roles_from_filmworks(person, related_filmworks)
            except ValidationError:
                logging.error(f"Error while validating {person_dict}")
            else:
                await self._put_to_cache(person)
        return person

    async def get_person_films(self, person_id: str, params: CommonQueryParams) -> list[Film]:
        person_filmworks = await self.film_service.get_person_films(person_id, params)
        return person_filmworks

    async def search(self, query: str, params: CommonQueryParams) -> list[Person]:
        raw_persons = await self.search_service.text_search(
            search_query=query, search_fields=["full_name"], params=params
        )
        persons = [Person(**raw_person) for raw_person in raw_persons]
        for person in persons:
            related_filmworks = await self.film_service.get_person_films(
                person.id, params=CommonQueryParams(page_size=10000)
            )
            person.films = self._get_roles_from_filmworks(person, related_filmworks)
        return persons

    @staticmethod
    def _get_roles_from_filmworks(person: Person, person_filmworks: list[Film]) -> list[PersonFilm]:
        result: list[PersonFilm] = []
        for filmwork in person_filmworks:
            person_film = PersonFilm(id=filmwork.id)
            for role in PERSON_ROLES:
                if person.full_name in getattr(filmwork, f"{role}s_names"):
                    person_film.roles.append(role)
            result.append(person_film)
        return result


@lru_cache()
def get_person_service(cache: Cache = Depends(get_cache_service), elastic: AsyncElasticsearch = Depends(get_elastic), film_service: FilmService = Depends(get_film_service),
) -> PersonService:
    return PersonService(
        cache, search_service=ElasticSearchService(elastic, index="persons"), film_service=film_service
    )
