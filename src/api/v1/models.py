from pydantic import BaseModel


class FilmShortModel(BaseModel):
    id: str
    title: str
    imdb_rating: float = 0.0


class Genre(BaseModel):
    id: str
    name: str


class Person(BaseModel):
    id: str
    full_name: str
    roles: list[str] = ['']
    film_ids: list[str] = ['']
