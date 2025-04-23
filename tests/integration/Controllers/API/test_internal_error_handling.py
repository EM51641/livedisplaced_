"""
This module contains unit tests for the error_handling module.
The TestHandleErrorRequest class contains test cases for the
handle_error_request function. The handle_error_request function is
responsible for handling internal server errors.
"""

import logging

import pytest
from quart.typing import TestClientProtocol as MockClientProtocol


@pytest.mark.asyncio
async def test_handle_internal_error_response(
    client: MockClientProtocol,
) -> None:
    """
    Test the handle_internal_error_request function in the error_handling
    module. The function should return a tuple containing a string and a
    status code.
    """
    response = await client.get("/internal_error")
    data = await response.get_data(as_text=True)
    code = response.status_code
    assert data == "Something went wrong.\nWe are troubleshooting the issue"
    assert code == 500


@pytest.mark.asyncio
async def test_handle_internal_error_log(client: MockClientProtocol, caplog) -> None:
    with caplog.at_level(logging.ERROR, logger="src.Controllers.Exceptions"):
        await client.get("/internal_error")
    assert caplog.record_tuples == [
        (
            "src.Controllers.Exceptions",
            logging.ERROR,
            "Oups something wrong happened.",
        )
    ]
    assert caplog.records[0].stack_info is not None
    assert caplog.records[0].exc_text is not None
