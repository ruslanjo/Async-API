from .mixins import BaseMixin
from uuid import UUID
from pydantic import BaseModel


class Genre(BaseModel):
    id: bytes
    name: str = ''
