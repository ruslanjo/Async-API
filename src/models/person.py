from .mixins import BaseMixin


class Person(BaseMixin):
    id: str
    full_name: str
    roles: list[str] = ['']
    film_ids: list[str] = ['']
