from abc import ABC, abstractmethod
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.Context.Domain.TermsOfUse import SignedTermsOfUse, TermsOfUse
from src.Context.Service import ServiceBase
from src.Context.Service.UnitOfWork.TermsOfUse import TermsOfUseUnitOfWork


class BaseUserComplianceService(ServiceBase[TermsOfUseUnitOfWork]):
    @abstractmethod
    async def make_user_compliant(self, user_id: UUID) -> None:
        """Not implemented yet"""


class UserComplianceService(BaseUserComplianceService):
    async def make_user_compliant(self, user_id: UUID) -> None:
        """
        Make a user compliant with the terms of use.

        Params:
        ----
            user: The user domain.

        Returns:
        ----
            SignedTermsOfUse
        """
        last_released_term = (
            await self._unit_of_work.terms_of_use_repository.find_latest_version()  # noqa
        )
        self._generate_new_agreement_and_add_to_session(user_id, last_released_term)
        await self._unit_of_work.save()

    def _generate_new_agreement_and_add_to_session(
        self, user_id: UUID, term: TermsOfUse
    ):
        """
        Generate a new agreement and save it.

        Params:
        ----
            use: The user.
            term: The terms of use.

        Returns:
        ----
            SignedTermsOfUse: The new agreement.
        """
        new_agreement = self._generate_new_agreement(user_id, term)
        self._unit_of_work.signed_terms_of_use_repository.add(new_agreement)
        return new_agreement

    def _generate_new_agreement(
        self, user_id: UUID, term: TermsOfUse
    ) -> SignedTermsOfUse:
        """
        Generate a new agreement.

        Params:
        ----
            user: The user domain.
            term: The terms of use domain.

        Returns:
        ----
            SignedTermsOfUse: The new agreement.
        """
        return SignedTermsOfUse(
            id=uuid4(), user_id=user_id, termsofuse_id=term.id, signed=datetime.now(UTC)
        )


class BaseUserCompliancePermissionService(ServiceBase[TermsOfUseUnitOfWork], ABC):
    @abstractmethod
    async def is_user_compliant(self, user_id: UUID) -> bool:
        """Not implemented yet"""


class UserCompliancePermissionService(BaseUserCompliancePermissionService):
    async def is_user_compliant(self, user_id: UUID) -> bool:
        """
        Check if the user is compliant with the terms of use.

        Params:
        ----
            user_id: The user id.

        Returns:
        ----
            bool: True if the user is compliant, False otherwise.
        """
        last_released_term = await self._get_latest_term()
        latest_signed_term_user = await self._get_latest_signed_term_per_user(user_id)
        return latest_signed_term_user.termsofuse_id == last_released_term.id

    async def _get_latest_term(self) -> TermsOfUse:
        """
        Retrieves the latest version of the Terms of Use.

        Returns:
            The latest version of the Terms of Use.
        """

        last_released_term = (
            await self._unit_of_work.terms_of_use_repository.find_latest_version()  # noqa
        )
        return last_released_term

    async def _get_latest_signed_term_per_user(self, user_id: UUID) -> SignedTermsOfUse:
        """
        Retrieves the latest signed terms of use for a given user.

        Args:
            user (User): The user for whom to retrieve the latest signed terms of use.

        Returns:
            SignedTermsOfUse: The latest signed terms of use for the user.
        """
        last_signed_term = await self._unit_of_work.signed_terms_of_use_repository.find_latest_compliant_term_per_user(
            user_id
        )
        return last_signed_term
