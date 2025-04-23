"""
The User and Account models are all here
"""

from __future__ import annotations

import datetime
from abc import abstractmethod
from typing import TYPE_CHECKING
from uuid import UUID

from src.Context.Domain import BusinessObject

if TYPE_CHECKING:
    from typing import TypedDict, Union

    TLinkedToken = dict[str, Union[str, int, datetime.datetime]]

    class TOauthDomainDict(TypedDict):
        id: UUID
        user_id: UUID
        provider: str
        provider_user_id: str


class OauthBusinessObject(BusinessObject):
    @property
    @abstractmethod
    def provider(self) -> str:
        """Not implemented yet"""

    @property
    @abstractmethod
    def provider_user_id(self) -> str:
        """Not implemented yet"""

    @property
    @abstractmethod
    def user_id(self) -> UUID:
        """Not implemented yet"""


class Oauth(OauthBusinessObject):
    """
    Oauth Business Object
    """

    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        provider: str,
        provider_user_id: str,
    ) -> None:
        """
        Initialise the oauth object

        Params:
        ----
            record: OAuthModel

        Returns:
        ----
            None
        """
        super().__init__(id)
        self._user_id = user_id
        self._provider = provider
        self._provider_user_id = provider_user_id

    @property
    def provider(self) -> str:
        """
        Return the id of the oauth
        """
        return self._provider

    @property
    def provider_user_id(self) -> str:
        """
        Return the id of the oauth
        """
        return self._provider_user_id

    @property
    def user_id(self) -> UUID:
        """
        Return the id of the user account
        """
        return self._user_id

    def to_dict(self) -> TOauthDomainDict:
        """
        Return the user as a dictionary.

        Parameters:
        ----
            None

        Returns:
        ----
            TOauthDomainDict
        """
        return {
            "id": self._id,
            "user_id": self._user_id,
            "provider": self._provider,
            "provider_user_id": self._provider_user_id,
        }

    def __str__(self) -> str:
        return (
            f"Oauth(id={self._id}, user_id={self._user_id}, "
            f"provider={self._provider}, provider_user_id={self._provider_user_id})"  # noqa: E501
        )

    def __repr__(self) -> str:
        return (
            f"Oauth(id={repr(self._id)}, user_id={repr(self._user_id)}, "
            f"provider={repr(self._provider)}, provider_user_id={repr(self._provider_user_id)})"  # noqa: E501
        )
