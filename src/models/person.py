from uuid import UUID
from .mixins import BaseMixin


class Person(BaseMixin):
    id: str
    full_name: str
