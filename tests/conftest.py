"""PyTest configuration file.

Contains globally used fixtures for the unit testing.
"""

import pytest

from fastapi.testclient import TestClient

from my_rest_api.app import app


@pytest.fixture(scope='session')
def api_client() -> TestClient:
    """Return a TestClient instance for the FastAPI application.

    Returns:
        TestClient: A TestClient instance for the FastAPI application.
    """
    return TestClient(app)
