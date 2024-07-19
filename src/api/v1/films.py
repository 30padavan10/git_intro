from enum import Enum
from http import HTTPStatus
from typing import Annotated, Optional, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel

from models.model import Film
from services.film import FilmService, get_film_service
from services.genre import GenreService, get_genre_service
from utils.params import CommonQueryParams

router = APIRouter()


class FilmPerson(BaseModel):
    """Output schema for film actors, writers, directors"""

    uuid: str
    full_name: str


class FilmGenre(BaseModel):
    """Output schema for film genre"""

    uuid: str
    name: str


class FilmOut(BaseModel):
    """Output schema for film detail"""

    uuid: str
    title: str
    description: Optional[str] = None
    imdb_rating: Optional[float]
    genre: list[FilmGenre]
    actors: list[FilmPerson]
    writers: list[FilmPerson]
    directors: list[FilmPerson]


class FilmShortOut(BaseModel):
    """Output schema for films in list endpoints"""

    uuid: str
    title: str
    imdb_rating: Optional[float]


class TypeSort(str, Enum):
    """Types of sort for films"""

    imdb_rating = "imdb_rating"


@router.get(
    "/{film_id}",
    summary="Информация о фильме",
    response_model=FilmOut,
)
async def film_details(
    film_id: Annotated[str, Path(description="ID фильма в форматее UUID")],
    film_service: FilmService = Depends(get_film_service),
    genre_service: GenreService = Depends(get_genre_service),
) -> FilmOut:
    """
    Получить полную информацию о фильме с переданным id.

    **Параметры запроса**:
    - `film_id` - строка в формате UUID.

    **Возвращает**:
    - Полную информацию о фильме с переданным id.

    **Возбуждает исключения**:
    - `HTTPException`, если фильм с заданным id не был найден в базе данных.
    """
    film = cast(Film | None, await film_service.get_by_id(film_id))
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    genres = [await genre_service.get_by_text_field("name", name) for name in film.genres]
    return FilmOut(
        uuid=film.id,
        title=film.title,
        description=film.description,
        imdb_rating=film.imdb_rating,
        genre=[FilmGenre(uuid=g.id, name=g.name) for g in genres if g is not None],
        actors=[FilmPerson(uuid=p.id, full_name=p.name) for p in film.actors],
        writers=[FilmPerson(uuid=p.id, full_name=p.name) for p in film.writers],
        directors=[FilmPerson(uuid=p.id, full_name=p.name) for p in film.directors],
    )


@router.get(
    "/",
    summary="Список фильмов",
    response_model=list[FilmShortOut],
)
async def films(
    query_params: Annotated[CommonQueryParams, Depends()],
    genre_uuid: Annotated[
        str | None,
        Query(alias="genre", description="Фильтрация по uuid жанра"),
    ] = None,
    film_service: FilmService = Depends(get_film_service),
    genre_service: GenreService = Depends(get_genre_service),
) -> list[FilmShortOut]:
    """
    Получить список фильмов.

    **Параметры запроса:**
    - `page_size` - натуральное число, количество фильмов на одной странице. Значение по умолчанию - 10.
    - `page_number` - натуральное число, номер страницы с фильмами. Значение по умолчанию - 1.
    - `sort` - строка в формате `-field_name`, где наличие `-` соответствует сортировке по полю `field_name`
               в порядке по убыванию (DESC), а отсутствие - по возрастанию (ASC). Параметр можно передать
               несколько раз, с разными значениями для сортировки по нескольким полям.
    - `genre` - строка в формате UUID, id жанра. При использовании этого поля будут возвращены только
               фильмы указанного жанра. По умолчанию возвращаются фильмы всех жанров.

    **Возбуждает исключения**:
    - `HTTPException`, если был передан параметр `genre_uuid`, и указанный жанр не был найден в базе данных.
    """
    genre = None
    if genre_uuid:
        genre = await genre_service.get_by_id(genre_uuid)
        if not genre:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")
    films = await film_service.get_films(query_params, genre)
    return [FilmShortOut(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating) for film in films]


@router.get("/search/", summary="Поиск фильма", response_model=list[FilmShortOut])
async def search(
    query_params: Annotated[CommonQueryParams, Depends()],
    query: Annotated[
        str,
        Query(description="Запрос для полнотекстового поиска"),
    ],
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmShortOut]:
    """
    Полнотекстовый поиск фильмов по названию и описанию.

    **Параметры запроса:**
    - `query` - строка поискового запроса.
    - `page_size` - натуральное число, количество фильмов на одной странице. Значение по умолчанию - 10.
    - `page_number` - натуральное число, номер страницы с фильмами. Значение по умолчанию - 1.
    - `sort` - строка в формате `-field_name`, где наличие `-` соответствует сортировке по полю `field_name`
               в порядке по убыванию (DESC), а отсутствие - по возрастанию (ASC). Параметр можно передать
               несколько раз, с разными значениями для сортировки по нескольким полям.

    """
    films = await film_service.search(query, query_params)
    return [FilmShortOut(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating) for film in films]
