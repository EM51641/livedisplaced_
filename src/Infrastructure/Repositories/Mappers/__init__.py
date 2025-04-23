"""
Global Mappers
"""

from typing import Generic, TypeVar
from abc import ABC, abstractmethod
from src.Context.Domain import BusinessObject
from src.Infrastructure.Entities import BaseEntity


TEntity = TypeVar("TEntity", bound=BaseEntity)
TDomain = TypeVar("TDomain", bound=BusinessObject)


class EntityDomainMapper(ABC, Generic[TEntity, TDomain]):
    """
    Repository Pattern.
    """

    @abstractmethod
    def to_domain(self, entity: TEntity) -> TDomain:
        "Not implemented yet"

    @abstractmethod
    def to_entity(self, domain: TDomain) -> TEntity:
        "Not implemented yet"

    @abstractmethod
    def map_to_entity(self, domain: TDomain, entity: TEntity) -> None:
        "Not implemented yet"
