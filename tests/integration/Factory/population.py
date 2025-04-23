from datetime import datetime
from uuid import UUID

from src.Infrastructure.Entities.Population import DisplacedCategory, PopulationEntity
from tests.integration.Factory import BaseFactory


class PopulationFactory(BaseFactory):
    """
    Factory class for creating PopulationEntity objects.
    """

    async def create_population(
        self,
        country_id: UUID,
        country_arrival_id: UUID,
        id: UUID | None = None,
        number: int | None = None,
        year: int | None = None,
        category: DisplacedCategory | None = None,
        created: datetime | None = None,
    ) -> PopulationEntity:
        """
        Create a new PopulationEntity object with the given attributes.

        Args:
            country_id (UUID):
                The ID of the country.
            country_arrival_id (UUID):
                The ID of the country of arrival.
            id (UUID | None):
                The ID of the population entity. If None, a random UUID will be generated.
            number (int | None):
                The number of displaced people. If None, a random number will be generated.
            year (int | None):
                The year of the population data. If None, a random year will be generated.
            category (DisplacedCategory | None):
                The category of displaced people. If None, a random category will be generated.
            created (datetime | None):
                The creation date of the population data. If None, a random datetime will be generated.
        """
        if id is None:
            id = self._faker.unique.uuid4()

        if year is None:
            year = self._faker.random_int(min=2000, max=2021, step=1)

        if number is None:
            number = self._faker.random_int(min=0, step=1)

        if category is None:
            category = self._faker.random_element(DisplacedCategory)

        if created is None:
            created = self._faker.date_time_this_decade()

        population = PopulationEntity(
            id=id,  # type: ignore
            country_id=country_id,
            country_arrival_id=country_arrival_id,
            number=number,  # type: ignore
            year=year,  # type: ignore
            category=category,  # type: ignore
            created=created,  # type: ignore
        )

        self._session.add(population)
        await self._session.commit()
        return population
