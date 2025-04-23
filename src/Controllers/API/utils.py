from quart import abort
from quart.views import MethodView

from src.Infrastructure.Entities.Population import DisplacedCategory


class BaseAPIView(MethodView):
    """
    Base class for API views per category.
    """

    def _get_category(self, category_name: str):
        """
        Get the category based on the given category name.

        Args:
            category_name (str): The name of the category.

        Returns:
            DisplacedCategory: The category object.

        Raises:
            HTTPException: If the category name is not found.
        """
        try:
            category = DisplacedCategory[category_name]
        except KeyError:
            abort(404)
        return category
