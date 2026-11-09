"""
Automated Test Suite for PUT /users/{user_id} and PATCH /users/{user_id} endpoints.
Validates complete user replacement, partial updates, 404 on missing records,
email conflicts (409), empty payload checks (400), and authorization requirements.
"""

from typing import Any, Dict
import pytest
from utils.api_client import APIClient
from utils.helpers import assert_status_code, generate_random_email


@pytest.mark.functional
@pytest.mark.regression
class TestUpdateUsers:
    """Test suite covering full and partial user updates."""

    @pytest.mark.smoke
    def test_put_update_user_full_success(
        self,
        authenticated_client: APIClient,
        created_user: Dict[str, Any]
    ):
        """
        Verify PUT /users/{user_id} completely updates user fields and returns HTTP 200.
        """
        user_id = created_user["id"]
        updated_payload = {
            "name": "Updated Name Full",
            "email": generate_random_email(prefix="updated_full"),
            "role": "admin",
            "status": "inactive",
            "age": 40
        }

        response = authenticated_client.put(f"/users/{user_id}", json=updated_payload)
        assert_status_code(response, 200)

        body = response.json()
        assert body["id"] == user_id
        assert body["name"] == updated_payload["name"]
        assert body["email"] == updated_payload["email"]
        assert body["role"] == updated_payload["role"]
        assert body["status"] == updated_payload["status"]
        assert body["age"] == updated_payload["age"]

    @pytest.mark.negative
    def test_put_update_nonexistent_user_returns_404(self, authenticated_client: APIClient):
        """
        Verify PUT on non-existent user ID returns HTTP 404 Not Found.
        """
        non_existent_id = 88888
        payload = {
            "name": "Ghost User",
            "email": "ghost@example.com",
            "role": "tester",
            "status": "active",
            "age": 30
        }
        response = authenticated_client.put(f"/users/{non_existent_id}", json=payload)
        assert_status_code(response, 404)

        body = response.json()
        assert "detail" in body
        assert f"User with ID {non_existent_id} not found" in body["detail"]

    @pytest.mark.negative
    def test_put_update_duplicate_email_conflict_returns_409(
        self,
        authenticated_client: APIClient,
        created_user: Dict[str, Any]
    ):
        """
        Verify PUT attempting to change email to one already owned by another user returns HTTP 409.
        """
        user_id = created_user["id"]
        conflict_payload = {
            "name": "Conflicting Alice",
            "email": "alice@example.com",  # Belongs to user 1
            "role": "tester",
            "status": "active",
            "age": 28
        }
        response = authenticated_client.put(f"/users/{user_id}", json=conflict_payload)
        assert_status_code(response, 409)

        body = response.json()
        assert "detail" in body
        assert "already in use by another user" in body["detail"]

    @pytest.mark.smoke
    def test_patch_update_single_field_role(
        self,
        authenticated_client: APIClient,
        created_user: Dict[str, Any]
    ):
        """
        Verify PATCH /users/{user_id} updates a single field while leaving others unchanged.
        """
        user_id = created_user["id"]
        original_name = created_user["name"]
        original_email = created_user["email"]

        patch_payload = {"role": "developer"}
        response = authenticated_client.patch(f"/users/{user_id}", json=patch_payload)
        assert_status_code(response, 200)

        body = response.json()
        assert body["id"] == user_id
        assert body["role"] == "developer"
        # Verify unchanged fields remain preserved
        assert body["name"] == original_name
        assert body["email"] == original_email

    def test_patch_update_multiple_fields(
        self,
        authenticated_client: APIClient,
        created_user: Dict[str, Any]
    ):
        """
        Verify PATCH /users/{user_id} correctly updates multiple specific fields.
        """
        user_id = created_user["id"]
        patch_payload = {
            "name": "Partially Patched Name",
            "status": "inactive",
            "age": 55
        }
        response = authenticated_client.patch(f"/users/{user_id}", json=patch_payload)
        assert_status_code(response, 200)

        body = response.json()
        assert body["name"] == patch_payload["name"]
        assert body["status"] == patch_payload["status"]
        assert body["age"] == patch_payload["age"]

    @pytest.mark.negative
    def test_patch_update_nonexistent_user_returns_404(self, authenticated_client: APIClient):
        """
        Verify PATCH on non-existent user returns HTTP 404 Not Found.
        """
        non_existent_id = 77777
        response = authenticated_client.patch(f"/users/{non_existent_id}", json={"name": "Ghost"})
        assert_status_code(response, 404)

    @pytest.mark.negative
    def test_patch_update_empty_payload_returns_400(
        self,
        authenticated_client: APIClient,
        created_user: Dict[str, Any]
    ):
        """
        Verify PATCH with empty JSON object returns HTTP 400 Bad Request.
        """
        user_id = created_user["id"]
        response = authenticated_client.patch(f"/users/{user_id}", json={})
        assert_status_code(response, 400)

        body = response.json()
        assert "detail" in body
        assert "Empty patch payload" in body["detail"]

    @pytest.mark.negative
    def test_patch_update_invalid_data_type_returns_422(
        self,
        authenticated_client: APIClient,
        created_user: Dict[str, Any]
    ):
        """
        Verify PATCH with invalid data type for field (string for age) returns HTTP 422.
        """
        user_id = created_user["id"]
        response = authenticated_client.patch(f"/users/{user_id}", json={"age": "thirty"})
        assert_status_code(response, 422)

    @pytest.mark.auth
    @pytest.mark.negative
    def test_update_user_without_auth_returns_401(
        self,
        api_client: APIClient,
        created_user: Dict[str, Any]
    ):
        """
        Verify unauthenticated requests to PUT/PATCH return HTTP 401 Unauthorized.
        """
        user_id = created_user["id"]
        response_put = api_client.put(f"/users/{user_id}", json={"name": "No Auth"})
        assert_status_code(response_put, 401)

        response_patch = api_client.patch(f"/users/{user_id}", json={"name": "No Auth"})
        assert_status_code(response_patch, 401)
