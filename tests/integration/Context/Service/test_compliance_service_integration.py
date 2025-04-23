from datetime import timedelta
from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from src.Context.Service.TermsOfUse import (
    UserCompliancePermissionService,
    UserComplianceService,
)
from src.Context.Service.UnitOfWork.TermsOfUse import TermsOfUseUnitOfWork
from src.Context.Service.Utils.session import Session
from src.Infrastructure.Database import DBSession
from src.Infrastructure.Entities.TermsOfUse import (
    SignedTermsOfUseEntity,
    TermsOfUseEntity,
)
from tests.integration.conftest import resolve_query_one
from tests.integration.Factory.termsofuse import (
    SignedTermsOfUseFactory,
    TermsOfUseFactory,
)
from tests.integration.Factory.user import UserFactory


class BaseTestUserCompliance:

    @pytest_asyncio.fixture
    async def initial_terms_of_use(
        self, terms_of_use_factory: TermsOfUseFactory
    ) -> TermsOfUseEntity:
        """
        Create a terms of use.
        """
        terms_of_use = await terms_of_use_factory.create_terms_of_use()
        return terms_of_use

    @pytest_asyncio.fixture
    async def compliant_user_id(
        self,
        user_factory: UserFactory,
        signed_terms_of_use_factory: SignedTermsOfUseFactory,
        initial_terms_of_use: TermsOfUseEntity,
    ) -> UUID:
        """
        Create a compliant user.
        """
        user = await user_factory.create_user()
        await signed_terms_of_use_factory.create_signed_terms_of_use(
            user_id=user.id, termsofuse_id=initial_terms_of_use.id
        )
        return user.id

    @pytest_asyncio.fixture
    async def updated_terms_of_use(
        self,
        initial_terms_of_use: TermsOfUseEntity,
        terms_of_use_factory: TermsOfUseFactory,
    ) -> TermsOfUseEntity:
        """
        Create a terms of use.
        """
        terms_of_use = await terms_of_use_factory.create_terms_of_use(
            creation_date=initial_terms_of_use.created + timedelta(days=1)
        )
        return terms_of_use

    @pytest_asyncio.fixture
    async def non_compliant_anymore_user_id(
        self,
        user_factory: UserFactory,
        signed_terms_of_use_factory: SignedTermsOfUseFactory,
        initial_terms_of_use: TermsOfUseEntity,
        updated_terms_of_use,
    ) -> UUID:
        """
        Create a compliant user.
        """
        user = await user_factory.create_user()
        await signed_terms_of_use_factory.create_signed_terms_of_use(
            user_id=user.id, termsofuse_id=initial_terms_of_use.id
        )
        return user.id


class TestUserComplianceService(BaseTestUserCompliance):

    @pytest.fixture(autouse=True)
    def setup_service(self, scoped_session: async_scoped_session[AsyncSession]) -> None:
        """
        Setup the test on the TermsOfUseReset instance.
        """
        unit_of_work = TermsOfUseUnitOfWork(
            session=Session(), db_con=DBSession(scoped_session)
        )
        self._service = UserComplianceService(unit_of_work)

    @pytest.mark.asyncio
    async def test_make_past_user_compliant(
        self,
        session: AsyncSession,
        non_compliant_anymore_user_id: UUID,
        updated_terms_of_use: TermsOfUseEntity,
    ) -> None:
        """
        Test the make_user_compliant method.
        """
        await self._service.make_user_compliant(user_id=non_compliant_anymore_user_id)
        query = select(SignedTermsOfUseEntity).where(
            SignedTermsOfUseEntity.user_id == non_compliant_anymore_user_id,
            SignedTermsOfUseEntity.termsofuse_id == updated_terms_of_use.id,
        )
        signed_term = await resolve_query_one(query, session)
        assert signed_term.user_id == non_compliant_anymore_user_id
        assert signed_term.termsofuse_id == updated_terms_of_use.id


class TestUserCompliancePermissionService(BaseTestUserCompliance):

    @pytest.fixture(autouse=True)
    def setup_service(self, scoped_session: async_scoped_session[AsyncSession]) -> None:
        """
        Setup the test on the TermsOfUseReset instance.
        """
        unit_of_work = TermsOfUseUnitOfWork(
            session=Session(), db_con=DBSession(scoped_session)
        )
        self._service = UserCompliancePermissionService(unit_of_work)

    @pytest.mark.asyncio
    async def test_non_compliant_user(
        self, non_compliant_anymore_user_id: UUID
    ) -> None:
        """
        Test the is_user_compliant method.
        """
        is_compliant = await self._service.is_user_compliant(
            user_id=non_compliant_anymore_user_id
        )
        assert is_compliant is False

    @pytest.mark.asyncio
    async def test_compliant_user(self, compliant_user_id: UUID) -> None:
        """
        Test the is_user_compliant method.
        """
        is_compliant = await self._service.is_user_compliant(user_id=compliant_user_id)
        assert is_compliant is True
