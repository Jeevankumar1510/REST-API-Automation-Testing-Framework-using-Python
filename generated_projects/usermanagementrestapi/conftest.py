"""
Pytest configuration and global fixtures.
"""
import pytest
from config.config import BASE_URL, DEFAULT_TIMEOUT
from utils.api_client import APIClient

@pytest.fixture(scope="session")
def client() -> APIClient:
    return APIClient(base_url=BASE_URL, timeout=DEFAULT_TIMEOUT)
