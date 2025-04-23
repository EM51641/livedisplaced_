"""
Base class for all factories.
"""

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from faker import Faker

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class BaseFactory(ABC):
    seed = 10

    def __init__(self, session: AsyncSession):
        self._session = session
        self._faker = Faker()
