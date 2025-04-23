class IncorrectInput(Exception):
    """
    Exception when the input is incorrect.
    """

    def __init__(self, errors: dict[str, str]) -> None:
        """
        Parameters:
        ----
            :param message: message.
        """
        self.errors = errors
