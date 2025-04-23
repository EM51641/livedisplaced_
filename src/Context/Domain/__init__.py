"""
The business Object is put there
"""

from abc import ABC, abstractmethod
from typing import Any, TypeVar, TypedDict
from uuid import UUID


class BusinessObject(ABC):
    def __init__(self, id: UUID) -> None:
        self._id = id

    @abstractmethod
    def to_dict(self) -> Any:
        """Not implemented yet"""

    @property
    def id(self) -> UUID:
        return self._id


TDomain = TypeVar("TDomain", bound=BusinessObject)


class BaseDomainDict(TypedDict):
    id: UUID


TBaseDomainDict = TypeVar("TBaseDomainDict", bound=BaseDomainDict)
