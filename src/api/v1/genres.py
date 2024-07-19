from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field

from services.genre import GenreService, get_genre_service
from utils.params import CommonQueryParams

router = APIRouter()


class GenreSchema(BaseModel):
    uuid: str = Field(validation_alias="id")
    name: str
    description: str | None


@router.get(
    "/",
    summary="Список жанров",
    response_model=list[GenreSchema],
)
async def genre_list(
    params: Annotated[CommonQueryParams, Depends()],
    genre_service: GenreService = Depends(get_genre_service),
):
    """
    Получить список жанров.

    **Параметры запроса:**
    - `page_size` - натуральное число, количество жанров на одной странице. Значение по умолчанию - 10.
    - `page_number` - натуральное число, номер страницы с жанрами. Значение по умолчанию - 1.
    - `sort` - строка в формате `-field_name`, где наличие `-` соответствует сортировке по полю `field_name`
               в порядке по убыванию (DESC), а отсутствие - по возрастанию (ASC). Параметр можно передать
               несколько раз, с разными значениями для сортировки по нескольким полям.

    **Возбуждает исключения**:
    - `HTTPException`, если в базе данных нет ни одного жанра.
    """
    return await genre_service.get_list(params)


@router.get(
    "/{genre_id}",
    summary="Данные жанра",
    response_model=GenreSchema,
)
async def genre_details(
    genre_id: Annotated[str, Path(description="ID жанра в формате UUID")],
    genre_service: GenreService = Depends(get_genre_service),
):
    """
    Получить полную информацию о жанре.

    **Параметры запроса**:
    - `genre_id` - строка в формате UUID.


    **Возбуждает исключения**:
    - `HTTPException`, если жанр с заданным id не был найден в базе данных.
    """
    if genre := await genre_service.get_by_id(genre_id):
        return genre
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")
