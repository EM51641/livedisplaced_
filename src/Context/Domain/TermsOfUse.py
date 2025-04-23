from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from src.Context.Domain import BusinessObject

if TYPE_CHECKING:
    from datetime import datetime
    from typing import TypedDict
    from uuid import UUID

    class TTermsOfUse(TypedDict):
        id: UUID
        created: datetime

    class TSignedTermsOfUse(TypedDict):
        id: UUID
        user_id: UUID
        termsofuse_id: UUID
        signed: datetime


class BaseTermsOfUse(BusinessObject):
    @property
    @abstractmethod
    def created(self) -> datetime:
        """Not implemented yet"""


class TermsOfUse(BaseTermsOfUse):
    """
    This object stores the terms of use information.
    """

    def __init__(self, id: UUID, created: datetime) -> None:
        """
        Initialise a terms of use object.

        Parameters:
        ----
            created: The terms of use record.
            uid: The terms of use id.

        Returns:
        ----
            None
        """
        super().__init__(id)
        self._created = created

    @property
    def created(self) -> datetime:
        return self._created

    def to_dict(self) -> TTermsOfUse:
        """
        Returns dictionary of the Terms of Use info.
        """
        return {"id": self._id, "created": self._created}

    def __str__(self) -> str:
        return f"TermsOfUse(id={self.id}, created={self._created})"

    def __repr__(self) -> str:
        return f"TermsOfUse(id={repr(self.id)}, created={repr(self._created)})"


class BaseSignedTermsOfUse(BusinessObject):
    @property
    @abstractmethod
    def termsofuse_id(self) -> UUID:
        """Not implemented yet"""

    @property
    @abstractmethod
    def user_id(self) -> UUID:
        """Not implemented yet"""

    @property
    @abstractmethod
    def signed(self) -> datetime:
        """Not implemented yet"""


class SignedTermsOfUse(BaseSignedTermsOfUse):
    """
    This object stores the signed user's terms.
    """

    def __init__(
        self, id: UUID, user_id: UUID, termsofuse_id: UUID, signed: datetime
    ) -> None:
        """
        Initialise a terms of use object.

        Parameters:
        ----
            created: The terms of use record.
            uid: The terms of use id.

        Returns:
        ----
            None
        """
        super().__init__(id)
        self._user_id = user_id
        self._termsofuse_id = termsofuse_id
        self._signed = signed

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def termsofuse_id(self) -> UUID:
        return self._termsofuse_id

    @property
    def signed(self) -> datetime:
        return self._signed

    def to_dict(self) -> TSignedTermsOfUse:
        """
        Returns dictionary of the Terms of Use info.
        """
        return {
            "id": self._id,
            "user_id": self._user_id,
            "termsofuse_id": self._termsofuse_id,
            "signed": self._signed,
        }

    def __str__(self) -> str:
        return (
            f"SignedTermsOfUse(id={self._id}, user_id={self._user_id}, "
            f"termsofuse_id={self._termsofuse_id}, signed={self._signed})"
        )

    def __repr__(self) -> str:
        return (
            f"SignedTermsOfUse(id={repr(self._id)}, user_id={repr(self._user_id)}, "
            f"termsofuse_id={repr(self._termsofuse_id)}, signed={repr(self._signed)})"  # noqa
        )
