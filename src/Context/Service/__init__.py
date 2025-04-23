from abc import ABC
from typing import Generic, TypeVar

from src.Context.Service.UnitOfWork import UnitOfWork
from src.Infrastructure.Repositories.Utils import DALBase

TUnitOfWork = TypeVar("TUnitOfWork", bound=UnitOfWork)


class _ServiceBase(ABC, Generic[TUnitOfWork]):
    pass


class ServiceBase(_ServiceBase[TUnitOfWork]):
    """
    A service that runs on a single unit of work.
    """

    def __init__(self, unit_of_work: TUnitOfWork) -> None:
        self._unit_of_work = unit_of_work


TService = TypeVar("TService", bound=ServiceBase)


TDAL = TypeVar("TDAL", bound=DALBase)


class BaseServiceDAL(ABC, Generic[TDAL]):
    def __init__(self, dal: TDAL) -> None:
        self._data_access_layer = dal
