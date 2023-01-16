from uuid import UUID
from .mixins import BaseMixin


class Person(BaseMixin):
    id: UUID
    full_name: str
