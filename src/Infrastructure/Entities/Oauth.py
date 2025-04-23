from uuid import UUID

from sqlalchemy import UUID as UUID_
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.Infrastructure.Entities import BaseEntity


class OAuthEntity(BaseEntity):
    """
    This class represents an OAuth entity, which stores user authentication
    information.

    Attributes:
    ----------
    user_id : UUID
        The ID of the linked user account.
    provider : str
        The OAuth provider (e.g. Google, Facebook).
    provider_user_id : str
        The unique identifier of the user by the provider.
    token : dict[str, Union[str, int, datetime.datetime]]
        The secret token given by the provider for each connection.
    """

    __tablename__ = "oauth"  # type: ignore

    user_id: Mapped[UUID] = mapped_column(
        UUID_(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    provider_user_id: Mapped[str] = mapped_column(String, nullable=False)
    provider = mapped_column(String(50), nullable=False)

    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        provider: str,
        provider_user_id: str,
    ) -> None:
        """
        Initializes a new instance of the Oauth class.

        Args:
            id (UUID): The unique identifier for the Oauth entity.
            user_id (UUID): The unique identifier for the associated user.
            provider (str): The provider name for the Oauth authentication.
            provider_user_id (str): The unique identifier for the user in the provider's system.
        """
        self.id = id
        self.user_id = user_id
        self.provider = provider
        self.provider_user_id = provider_user_id

    def __repr__(self) -> str:
        return f"OAuthEntity(id={self.id}, user_id={self.user_id}, provider={self.provider}, provider_user_id={self.provider_user_id})"  # noqa
