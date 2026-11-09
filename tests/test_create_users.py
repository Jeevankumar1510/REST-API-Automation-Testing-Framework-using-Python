"""
Automated Test Suite for POST /users endpoint.
Validates successful user creation, header presence, email uniqueness (409),
missing mandatory fields (422), invalid formats, and authentication checks.
"""

from typing import Any, Dict
import pytest
from utils.api_client import APIClient
from utils.helpers import assert_status_code, generate_random_email, generate_random_user


@pytest.mark.functional
@pytest.mark.regression
class TestCreateUsers:
    """Test suite for user creation operations."""

    @pytest.mark.smoke
    def test_create_user_success_201(self, authenticated_client: APIClient):
        """
        Verify POST /users creates a new user and returns HTTP 201 with populated ID and timestamps.
        """
        payload = generate_random_user(name="Grace Hopper", role="developer", status="active", age=36)
        response = authenticated_client.post("/users", json=payload)
        assert_status_code(response, 201)

        body = response.json()
        assert "id" in body and isinstance(body["id"], int)
        assert body["name"] == payload["name"]
        assert body["email"] == payload["email"]
        assert body["role"] == payload["role"]
        assert body["status"] == payload["status"]
        assert body["age"] == payload["age"]
        assert "created_at" in body

        # Clean up created user
        authenticated_client.delete(f"/users/{body['id']}")

    def test_create_user_response_headers(self, authenticated_client: APIClient):
        """
        Verify response headers on user creation contain Content-Type and Location URL.
        """
        payload = generate_random_user()
        response = authenticated_client.post("/users", json=payload)
        assert_status_code(response, 201)

        user_id = response.json()["id"]
        assert "application/json" in response.headers.get("Content-Type", "")
        assert response.headers.get("Location") == f"/users/{user_id}"

        # Clean up
        authenticated_client.delete(f"/users/{user_id}")

    @pytest.mark.negative
    def test_create_user_duplicate_email_returns_409(self, authenticated_client: APIClient):
        """
        Verify attempting to register a user with an already existing email returns HTTP 409 Conflict.
        """
        existing_email = "alice@example.com"
        payload = {
            "name": "Duplicate Alice",
            "email": existing_email,
            "role": "tester",
            "status": "active",
            "age": 30
        }
        response = authenticated_client.post("/users", json=payload)
        assert_status_code(response, 409)

        body = response.json()
        assert "detail" in body
        assert f"Email '{existing_email}' already registered" in body["detail"]

    @pytest.mark.negative
    def test_create_user_missing_required_fields(
        self,
        authenticated_client: APIClient,
        test_data: Dict[str, Any]
    ):
        """
        Verify creating user with missing mandatory fields returns HTTP 422 Unprocessable Entity.
        """
        cases = test_data["invalid_users_missing_fields"]
        for case in cases:
            response = authenticated_client.post("/users", json=case["payload"])
            assert response.status_code == case["expected_status"], (
                f"Failed scenario: {case['description']}. Expected {case['expected_status']}, "
                f"got {response.status_code} with body: {response.text}"
            )

    @pytest.mark.negative
    def test_create_user_invalid_email_format(
        self,
        authenticated_client: APIClient,
        test_data: Dict[str, Any]
    ):
        """
        Verify malformed email formats are rejected with HTTP 422.
        """
        cases = test_data["invalid_users_bad_email"]
        for case in cases:
            response = authenticated_client.post("/users", json=case["payload"])
            assert response.status_code == case["expected_status"], (
                f"Failed on bad email scenario: {case['description']}. Body: {response.text}"
            )

    @pytest.mark.negative
    def test_create_user_invalid_role(
        self,
        authenticated_client: APIClient,
        test_data: Dict[str, Any]
    ):
        """
        Verify non-whitelisted roles are rejected with HTTP 422.
        """
        cases = test_data["invalid_roles"]
        for case in cases:
            response = authenticated_client.post("/users", json=case["payload"])
            assert response.status_code == case["expected_status"], (
                f"Failed invalid role scenario: {case['description']}"
            )

    @pytest.mark.negative
    def test_create_user_age_boundary_validation(
        self,
        authenticated_client: APIClient,
        test_data: Dict[str, Any]
    ):
        """
        Verify age boundaries (<18 and >100) are enforced with HTTP 422.
        """
        cases = test_data["invalid_users_out_of_range"]
        for case in cases:
            response = authenticated_client.post("/users", json=case["payload"])
            assert response.status_code == case["expected_status"], (
                f"Boundary validation failed for {case['description']}"
            )

    @pytest.mark.auth
    @pytest.mark.negative
    def test_create_user_without_auth_returns_401(self, api_client: APIClient):
        """
        Verify unauthenticated requests to POST /users return HTTP 401 Unauthorized.
        """
        payload = generate_random_user()
        response = api_client.post("/users", json=payload)
        assert_status_code(response, 401)

        body = response.json()
        assert "detail" in body
        assert "Missing authentication token" in body["detail"]

