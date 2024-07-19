from typing import Optional

from pydantic import BaseModel, Field


class PersonFilm(BaseModel):
    id: str
    roles: list[str] = Field(default_factory=list)


class Person(BaseModel):
    id: str
    full_name: str
    films: list[PersonFilm] = Field(default_factory=list)


class Genre(BaseModel):
    id: str
    name: str
    description: str | None


class FilmPerson(BaseModel):
    id: str
    name: str


class Film(BaseModel):
    id: str
    title: str
    description: Optional[str]
    imdb_rating: Optional[float]
    actors: list[FilmPerson] = Field(default_factory=list)
    writers: list[FilmPerson] = Field(default_factory=list)
    directors: list[FilmPerson] = Field(default_factory=list)
    genres: list[str] = Field(default_factory=list)
    actors_names: list[str] = Field(default_factory=list)
    writers_names: list[str] = Field(default_factory=list)
    directors_names: list[str] = Field(default_factory=list)
