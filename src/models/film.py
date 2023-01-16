from .mixins import BaseMixin


class Film(BaseMixin):
    title: str
    description: str = ''
    imdb_rating: float = 0.0
    genre: list[str] = ['']
    directors: list[dict] = [{}]
    writers: list[dict] = [{}]
    actors: list[dict] = [{}]
    writers_names: list[str] = ['']
    directors_names: list[str] = ['']
    actors_names: list[str] = ['']
