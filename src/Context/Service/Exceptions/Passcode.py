class InvalidResetToken(Exception):
    """
    Exception when the reset passcode is not found.
    """

    def __init__(self, message: str = "Not found reset token") -> None:
        """
        Parameters:
        ----
            :param message: message.
        """
        super().__init__(message)


class InvalidActivationToken(Exception):
    """
    Exception when the token is invalid.
    """

    def __init__(self, message: str = "Invalid token") -> None:
        """
        Parameters:
        ----
            :param message: message.
        """
        super().__init__(message)
