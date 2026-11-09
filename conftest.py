"""
Pytest configuration and shared fixtures for the API Automation Framework.
Manages test fixtures, client initialization, server lifecycle, and HTML reporting hooks.
"""

from datetime import datetime, timezone
import json
import threading
import time
from typing import Any, Dict, Generator
import pytest
import requests
import uvicorn

from config.config import (
    LOG_FILE_PATH,
    USER_SCHEMA_PATH,
    USERS_TEST_DATA_PATH,
    settings
)
from utils.api_client import APIClient
from utils.helpers import generate_random_user, load_json
from utils.logger import get_logger

logger = get_logger("Conftest")


# ---------------------------------------------------------------------------
# Background Server Fixture (Ensures API is live before any test runs)
# ---------------------------------------------------------------------------
class ServerThread(threading.Thread):
    """Thread wrapper to run Uvicorn server in background during test session."""

    def __init__(self, host: str, port: int) -> None:
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        config = uvicorn.Config("application.main:app", host=host, port=port, log_level="warning")
        self.server = uvicorn.Server(config)

    def run(self) -> None:
        self.server.run()

    def stop(self) -> None:
        self.server.should_exit = True


@pytest.fixture(scope="session", autouse=True)
def ensure_server_running() -> Generator[None, None, None]:
    """
    Session-level fixture that verifies the FastAPI target server is reachable.
    If not already running, it boots Uvicorn in a background thread and waits for /health.
    """
    server_thread = None
    health_url = f"{settings.BASE_URL}/health"

    # Check if server is already responding
    already_running = False
    try:
        res = requests.get(health_url, timeout=1.0)
        if res.status_code == 200:
            already_running = True
            logger.info(f"Target API is already running at {settings.BASE_URL}")
    except requests.RequestException:
        already_running = False

    if not already_running:
        logger.info(f"Starting background FastAPI test server on {settings.HOST}:{settings.PORT}...")
        server_thread = ServerThread(host=settings.HOST, port=settings.PORT)
        server_thread.start()

        # Poll health endpoint until online (max 5 seconds)
        start_wait = time.time()
        while time.time() - start_wait < 5.0:
            try:
                res = requests.get(health_url, timeout=0.5)
                if res.status_code == 200:
                    logger.info("Background FastAPI server is healthy and ready for tests.")
                    break
            except requests.RequestException:
                time.sleep(0.1)
        else:
            raise RuntimeError(f"Could not connect to FastAPI server at {health_url} after 5 seconds.")

    # Reset database state before executing test session
    try:
        requests.post(f"{settings.BASE_URL}/reset-db", timeout=2.0)
    except Exception as exc:
        logger.warning(f"Could not reset database: {exc}")

    yield

    if server_thread:
        logger.info("Stopping background FastAPI test server...")
        server_thread.stop()
        server_thread.join(timeout=2.0)


# ---------------------------------------------------------------------------
# Reusable Client and Authentication Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def api_client() -> APIClient:
    """Provides a base unauthenticated APIClient instance."""
    return APIClient(base_url=settings.BASE_URL)


@pytest.fixture(scope="session")
def auth_token(api_client: APIClient) -> str:
    """
    Authenticates with valid test user credentials and yields JWT access token.
    """
    payload = {
        "username": settings.TEST_USER_USERNAME,
        "password": settings.TEST_USER_PASSWORD
    }
    response = api_client.post("/login", json=payload)
    assert response.status_code == 200, f"Authentication fixture failed: {response.text}"
    token = response.json()["access_token"]
    logger.info("Session auth_token acquired successfully.")
    return token


@pytest.fixture(scope="function")
def authenticated_client(auth_token: str) -> Generator[APIClient, None, None]:
    """
    Provides an APIClient instance with valid Bearer token pre-configured.
    """
    client = APIClient(base_url=settings.BASE_URL)
    client.set_bearer_token(auth_token)
    yield client
    client.clear_bearer_token()


@pytest.fixture(scope="function")
def created_user(authenticated_client: APIClient) -> Generator[Dict[str, Any], None, None]:
    """
    Fixture with automatic setup and teardown:
    1. Creates a random user before test execution.
    2. Yields the created user dictionary to the test.
    3. Deletes the created user after test completes.
    """
    user_payload = generate_random_user(name="Fixture Setup User", role="tester")
    response = authenticated_client.post("/users", json=user_payload)
    assert response.status_code == 201, f"Setup failed: unable to create test user: {response.text}"
    user_data = response.json()
    user_id = user_data["id"]
    logger.info(f"[SETUP] Created temporary user with ID={user_id} for test isolation.")

    yield user_data

    # Teardown
    delete_response = authenticated_client.delete(f"/users/{user_id}")
    if delete_response.status_code in (200, 404):
        logger.info(f"[TEARDOWN] Cleaned up temporary user ID={user_id}.")
    else:
        logger.warning(f"[TEARDOWN] Cleanup returned unexpected status {delete_response.status_code}.")


# ---------------------------------------------------------------------------
# Test Data and Schema Loaders
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def test_data() -> Dict[str, Any]:
    """Loads all test cases from test_data/users.json."""
    return load_json(USERS_TEST_DATA_PATH)


@pytest.fixture(scope="session")
def user_schema() -> Dict[str, Any]:
    """Loads JSON Schema definition for User entity."""
    return load_json(USER_SCHEMA_PATH)


# ---------------------------------------------------------------------------
# Pytest HTML Reporting Customizations
# ---------------------------------------------------------------------------
def pytest_html_report_title(report: Any) -> None:
    """Customize HTML report browser tab and main header."""
    report.title = "REST API Automation Test Execution Report"


def pytest_configure(config: Any) -> None:
    """Add environment and build metadata to HTML report summary."""
    if hasattr(config, "_metadata"):
        config._metadata["Project Name"] = "REST API Automation Testing Framework"
        config._metadata["Target API"] = settings.BASE_URL
        config._metadata["Environment"] = "Local / CI"
        config._metadata["Execution Time"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        config._metadata["Python Version"] = "3.12+"
        config._metadata["Report Type"] = "Pytest HTML Report"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: Any, call: Any) -> Generator[None, Any, None]:
    """
    Hook to capture test failures and inject detailed diagnostic logs into the HTML report.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # Attach failure details to report extras
        failure_summary = f"Test Failed: {item.nodeid}\nReason: {report.longreprtext[:600]}"
        try:
            from pytest_html import extras
            extra_item = extras.text(failure_summary, name="Failure Diagnostics")
            if hasattr(report, "extras"):
                report.extras.append(extra_item)
            elif hasattr(report, "extra"):
                report.extra.append(extra_item)
        except Exception:
            pass
