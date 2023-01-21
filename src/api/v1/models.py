from pydantic import BaseModel


class Film(BaseModel):
    id: str
    title: str
    imdb_rating: float = 0.0
    description: str = ''
    genre: list[str] = ['']
    directors: list[dict] = [{}]
    writers: list[dict] = [{}]
    actors: list[dict] = [{}]
    writers_names: list[str] = ['']
    directors_names: list[str] = ['']
    actors_names: list[str] = ['']


class FilmShortModel(BaseModel):
    id: str
    title: str
    imdb_rating: float = 0.0


class Genre(BaseModel):
    id: str
    name: str
