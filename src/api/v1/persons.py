from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field

from services.person import PersonService, get_person_service
from utils.params import CommonQueryParams

router = APIRouter()


class PersonFilmRoles(BaseModel):
    uuid: UUID = Field(validation_alias="id")
    roles: list[str]


class PersonDetails(BaseModel):
    uuid: UUID = Field(validation_alias="id")
    full_name: str
    films: list[PersonFilmRoles]


class PersonFilm(BaseModel):
    uuid: UUID = Field(validation_alias="id")
    title: str
    imdb_rating: float


@router.get(
    "/search",
    summary="Поиск по персонам",
    response_model=list[PersonDetails],
)
async def person_search(
    query: Annotated[str, Query(description="строка поискового запроса")],
    params: Annotated[CommonQueryParams, Depends()],
    person_service: PersonService = Depends(get_person_service),
):
    """
    Полнотекстовый поиск персон по имени.

    **Параметры запроса:**
    - `query` - строка поискового запроса.
    - `page_size` - натуральное число, количество персон на одной странице. Значение по умолчанию - 10.
    - `page_number` - натуральное число, номер страницы с персонами. Значение по умолчанию - 1.
    - `sort` - строка в формате `-field_name`, где наличие `-` соответствует сортировке по полю `field_name`
               в порядке по убыванию (DESC), а отсутствие - по возрастанию (ASC). Параметр можно передать
               несколько раз, с разными значениями для сортировки по нескольким полям.

    **Возвращает**:
    - Список данных о персонах в формате:
        ```json
        {
            "uuid": ...
            "full_name": ...
            "films": ...
        }
        ```

    **Возбуждает исключения**:
    - `HTTPException`, если не было найдено ни одной персоны релевантной запросу.
    """
    person = await person_service.search(query, params)
    return person


@router.get(
    "/{person_id}/films",
    summary="Фильмы персоны",
    response_model=list[PersonFilm],
)
async def person_filmworks(
    person_id: Annotated[str, Path(description="ID персоны в формате UUID")],
    params: Annotated[CommonQueryParams, Depends()],
    person_service: PersonService = Depends(get_person_service),
):
    """
    Получить список фильмов, в создании которых участвовала конкретная персона.

    **Параметры запроса:**
    - `person_id` - строка в формате UUID.
    - `page_size` - натуральное число, количество фильмов на одной странице. Значение по умолчанию - 10.
    - `page_number` - натуральное число, номер страницы с фильмами. Значение по умолчанию - 1.
    - `sort` - строка в формате `-field_name`, где наличие `-` соответствует сортировке по полю `field_name`
               в порядке по убыванию (DESC), а отсутствие - по возрастанию (ASC). Параметр можно передать
               несколько раз, с разными значениями для сортировки по нескольким полям.

    **Возбуждает исключения**:
    - `HTTPException`, если в базе данных нет информации о фильмах, созданных с участием данной персоны.
    """
    person_filmworks = await person_service.get_person_films(person_id, params)
    return person_filmworks


@router.get(
    "/{person_id}",
    summary="Данные персоны",
    response_model=PersonDetails,
)
async def person_details(
    person_id: Annotated[str, Path(description="ID персоны в формате UUID")],
    person_service: PersonService = Depends(get_person_service),
):
    """
    Получить полную информацию о персоне с переданным id.

    **Параметры запроса**:
    - `person_id` - строка в формате UUID.

    **Возбуждает исключения**:
    - `HTTPException`, если персона с заданным id не была найден в базе данных.
    """
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")
    return person
