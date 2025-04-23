import os
from abc import ABC, abstractmethod

from async_sendgrid import SendgridAPI  # type: ignore
from httpx._models import Response
from sendgrid.helpers.mail import Mail  # type: ignore


class BaseEmailManager(ABC):
    @property
    @abstractmethod
    def sendgrid(self) -> SendgridAPI:
        """Not implemented"""

    @abstractmethod
    async def send_email(self, email: Mail) -> None:
        """Not implemented"""


class EmailManager(BaseEmailManager):
    """
    Sendgrid API

    This class provides methods to send emails using the Sendgrid API.
    """

    def __init__(self, api_key: str | None = None, url: str | None = None):
        """
        Initializes a SendgridEmailSender object.

        Args:
            api_key (str | None):
                The Sendgrid API key. If None, it will be retrieved from the environment variable SENDGRID_API_KEY.
            url (str | None):
                The Sendgrid API endpoint URL. If None, the default endpoint will be used.
        """
        if not api_key:
            api_key = os.environ["SENDGRID_API_KEY"]

        if not url and os.environ.get("ENV"):
            url = os.environ["SENDGRID_TEST_URL"]

        self._sendgrid = SendgridAPI(api_key=api_key)

        if url:
            self._sendgrid._endpoint = url

    @property
    def sendgrid(self) -> SendgridAPI:
        """
        Returns the SendGrid client used for sending emails asynchronously.

        Returns:
            AsyncClient: The SendGrid client.
        """
        return self._sendgrid

    async def send_email(self, email: Mail) -> None:
        """
        Send Email.

        Parameters:
        ----
            email: Mail
                The email object containing the details of the email to be sent.

        Returns:
        ----
            dict[Any, Any]:
                The response from the Sendgrid API after sending the email.
        """

        response = await self._send_email(email)

        if response.status_code != 202:
            raise Exception(f"Email not sent: {response}")

    async def _send_email(self, email: Mail) -> Response:
        """
        Send Email.

        Parameters:
        ----
            email: Mail
                The email object containing the details of the email to be sent.

        Returns:
        ----
            dict[Any, Any]:
                The response from the Sendgrid API after sending the email.
        """

        async with self._sendgrid as client:
            response = await client.send(email)

        return response
