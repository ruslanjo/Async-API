import abc
from abc import ABC
from uuid import UUID


class BaseDAO(ABC):
    @abc.abstractmethod
    async def get_by_id(self, item_id: UUID):
        pass
