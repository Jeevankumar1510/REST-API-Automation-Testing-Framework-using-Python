"""
Automated Test Suite for Authentication and Token Lifecycle.
Tests POST /login, token generation, missing/invalid credentials,
and Bearer token authorization checks on protected endpoints.
"""

from typing import Any, Dict
import pytest
from config.config import settings
from utils.api_client import APIClient
from utils.helpers import assert_status_code


@pytest.mark.auth
@pytest.mark.regression
class TestAuthentication:
    """Test suite for authentication workflows and security boundaries."""

    @pytest.mark.smoke
    def test_login_success_with_valid_credentials(self, api_client: APIClient):
        """
        Verify POST /login with valid credentials returns HTTP 200, JWT access token, and bearer type.
        """
        payload = {
            "username": settings.TEST_USER_USERNAME,
            "password": settings.TEST_USER_PASSWORD
        }
        response = api_client.post("/login", json=payload)
        assert_status_code(response, 200)

        body = response.json()
        assert "access_token" in body and len(body["access_token"]) > 20
        assert body.get("token_type") == "bearer"
        assert body.get("expires_in") == 3600

    @pytest.mark.negative
    def test_login_failure_invalid_password(self, api_client: APIClient):
        """
        Verify POST /login with incorrect password returns HTTP 401 Unauthorized.
        """
        payload = {
            "username": settings.TEST_USER_USERNAME,
            "password": "CompletelyWrongPassword!"
        }
        response = api_client.post("/login", json=payload)
        assert_status_code(response, 401)

        body = response.json()
        assert "detail" in body
        assert "Invalid authentication credentials" in body["detail"]

    @pytest.mark.negative
    def test_login_failure_nonexistent_user(self, api_client: APIClient):
        """
        Verify POST /login with non-existent username returns HTTP 401 Unauthorized.
        """
        payload = {
            "username": "unknown_user_999@example.com",
            "password": "Password123!"
        }
        response = api_client.post("/login", json=payload)
        assert_status_code(response, 401)
        assert "Invalid authentication credentials" in response.json()["detail"]

    @pytest.mark.negative
    @pytest.mark.parametrize("missing_field", ["username", "password"])
    def test_login_missing_mandatory_fields(self, api_client: APIClient, missing_field: str):
        """
        Verify POST /login with missing username or password returns HTTP 422 Unprocessable Entity.
        """
        payload = {
            "username": "admin@example.com",
            "password": "AdminPass123!"
        }
        del payload[missing_field]

        response = api_client.post("/login", json=payload)
        assert_status_code(response, 422)

    def test_verify_token_endpoint_with_valid_token(
        self,
        api_client: APIClient,
        auth_token: str
    ):
        """
        Verify GET /auth/verify confirms identity when supplied with a valid Bearer token.
        """
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = api_client.get("/auth/verify", headers=headers)
        assert_status_code(response, 200)

        body = response.json()
        assert body.get("status") == "authenticated"
        assert body.get("user") == settings.TEST_USER_USERNAME

    @pytest.mark.negative
    def test_access_protected_endpoint_without_token(self, api_client: APIClient):
        """
        Verify accessing protected endpoint without Authorization header returns HTTP 401.
        """
        response = api_client.get("/auth/verify")
        assert_status_code(response, 401)
        assert "Missing authentication token" in response.json()["detail"]

    @pytest.mark.negative
    def test_access_protected_endpoint_with_invalid_token(self, api_client: APIClient):
        """
        Verify accessing protected endpoint with forged or invalid Bearer token returns HTTP 401.
        """
        headers = {"Authorization": "Bearer this.is.an.invalid.token.12345"}
        response = api_client.get("/auth/verify", headers=headers)
        assert_status_code(response, 401)
        assert "Invalid authentication token" in response.json()["detail"]

    @pytest.mark.negative
    def test_access_protected_endpoint_with_malformed_auth_header(self, api_client: APIClient):
        """
        Verify sending an Authorization header without the 'Bearer ' scheme prefix returns HTTP 401.
        """
        headers = {"Authorization": "Basic dXNlcjpwYXNz"}
        response = api_client.get("/auth/verify", headers=headers)
        assert_status_code(response, 401)
        assert "Invalid authentication scheme" in response.json()["detail"]
