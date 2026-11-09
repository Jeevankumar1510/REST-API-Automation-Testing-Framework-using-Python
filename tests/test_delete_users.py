"""
Automated Test Suite for DELETE /users/{user_id} endpoint.
Validates successful deletion, verification via subsequent GET (404),
deleting non-existent entities, invalid parameter types, and authorization controls.
"""

import pytest
from utils.api_client import APIClient
from utils.helpers import assert_status_code, generate_random_user


@pytest.mark.functional
@pytest.mark.regression
class TestDeleteUsers:
    """Test suite for user deletion operations."""

    @pytest.mark.smoke
    def test_delete_existing_user_success_200(self, authenticated_client: APIClient):
        """
        Verify DELETE /users/{user_id} deletes an active user and returns HTTP 200 with confirmation message.
        """
        # Step 1: Create a dedicated user for deletion
        user_payload = generate_random_user(name="User To Be Deleted", role="guest")
        create_res = authenticated_client.post("/users", json=user_payload)
        assert_status_code(create_res, 201)
        user_id = create_res.json()["id"]

        # Step 2: Delete the user
        delete_res = authenticated_client.delete(f"/users/{user_id}")
        assert_status_code(delete_res, 200)

        body = delete_res.json()
        assert body["deleted_user_id"] == user_id
        assert f"User {user_id} deleted successfully" in body["message"]

    def test_verify_deleted_user_cannot_be_retrieved(self, authenticated_client: APIClient):
        """
        Verify that a deleted user can no longer be retrieved via GET /users/{user_id} (returns 404).
        """
        user_payload = generate_random_user(name="Ephemeral User")
        create_res = authenticated_client.post("/users", json=user_payload)
        user_id = create_res.json()["id"]

        # Delete user
        del_res = authenticated_client.delete(f"/users/{user_id}")
        assert_status_code(del_res, 200)

        # Attempt to retrieve deleted user
        get_res = authenticated_client.get(f"/users/{user_id}")
        assert_status_code(get_res, 404)

    @pytest.mark.negative
    def test_delete_nonexistent_user_returns_404(self, authenticated_client: APIClient):
        """
        Verify attempting to delete a non-existent user ID returns HTTP 404 Not Found.
        """
        non_existent_id = 999999
        response = authenticated_client.delete(f"/users/{non_existent_id}")
        assert_status_code(response, 404)

        body = response.json()
        assert "detail" in body
        assert f"User with ID {non_existent_id} not found" in body["detail"]

    @pytest.mark.negative
    def test_delete_invalid_id_type_returns_422(self, authenticated_client: APIClient):
        """
        Verify passing a string identifier to DELETE returns HTTP 422 Unprocessable Entity.
        """
        response = authenticated_client.delete("/users/abc-not-an-id")
        assert_status_code(response, 422)

    @pytest.mark.auth
    @pytest.mark.negative
    def test_delete_user_without_authentication_returns_401(self, api_client: APIClient):
        """
        Verify unauthenticated requests to DELETE /users/{id} return HTTP 401 Unauthorized.
        """
        response = api_client.delete("/users/1")
        assert_status_code(response, 401)
        assert "Missing authentication token" in response.json()["detail"]

