"""
Automated Test Suite for GET /users and GET /users/{user_id} endpoints.
Validates status codes, response structure, query filtering, pagination, headers, and 404/422 responses.
"""

import pytest
from utils.api_client import APIClient
from utils.helpers import assert_status_code


@pytest.mark.functional
@pytest.mark.regression
class TestGetUsers:
    """Test suite for retrieving user collections and individual user records."""

    @pytest.mark.smoke
    def test_get_all_users_status_and_structure(self, api_client: APIClient):
        """
        Verify GET /users returns HTTP 200 and standard pagination envelope.
        """
        response = api_client.get("/users")
        assert_status_code(response, 200)

        body = response.json()
        assert "total" in body, "Response missing 'total' field"
        assert "page" in body, "Response missing 'page' field"
        assert "limit" in body, "Response missing 'limit' field"
        assert "data" in body, "Response missing 'data' field"
        assert isinstance(body["data"], list), "'data' field should be a list"
        assert body["total"] >= len(body["data"]), "Total count cannot be less than returned items"

    def test_get_all_users_response_headers(self, api_client: APIClient):
        """
        Verify GET /users response headers include Content-Type, pagination metadata, and processing time.
        """
        response = api_client.get("/users")
        assert_status_code(response, 200)

        # Content-Type assertion
        assert "application/json" in response.headers.get("Content-Type", "")

        # Custom header assertions
        assert "X-Total-Count" in response.headers, "Response header missing X-Total-Count"
        assert "X-Page-Number" in response.headers, "Response header missing X-Page-Number"
        assert "X-Process-Time-Ms" in response.headers, "Response header missing X-Process-Time-Ms"

    def test_get_users_pagination_parameters(self, api_client: APIClient):
        """
        Verify pagination query parameters 'page' and 'limit' are respected.
        """
        limit = 2
        response = api_client.get("/users", params={"page": 1, "limit": limit})
        assert_status_code(response, 200)

        body = response.json()
        assert body["page"] == 1
        assert body["limit"] == limit
        assert len(body["data"]) <= limit, f"Expected at most {limit} users, got {len(body['data'])}"

    @pytest.mark.parametrize("role", ["admin", "tester", "developer", "guest"])
    def test_get_users_filtering_by_role(self, api_client: APIClient, role: str):
        """
        Verify filtering users by role returns only users matching the requested role.
        """
        response = api_client.get("/users", params={"role": role})
        assert_status_code(response, 200)

        body = response.json()
        for user in body["data"]:
            assert user["role"] == role, f"User role {user['role']} does not match filter {role}"

    @pytest.mark.parametrize("status_filter", ["active", "inactive"])
    def test_get_users_filtering_by_status(self, api_client: APIClient, status_filter: str):
        """
        Verify filtering users by status returns only users matching the requested status.
        """
        response = api_client.get("/users", params={"status": status_filter})
        assert_status_code(response, 200)

        body = response.json()
        for user in body["data"]:
            assert user["status"] == status_filter, f"User status {user['status']} does not match {status_filter}"

    def test_get_users_search_query(self, api_client: APIClient):
        """
        Verify search parameter filters results matching name or email substring.
        """
        search_term = "Alice"
        response = api_client.get("/users", params={"search": search_term})
        assert_status_code(response, 200)

        body = response.json()
        assert body["total"] >= 1
        found = any(search_term.lower() in u["name"].lower() for u in body["data"])
        assert found, f"Search query '{search_term}' did not find matching user in data"

    @pytest.mark.smoke
    def test_get_user_by_valid_id(self, api_client: APIClient):
        """
        Verify GET /users/{user_id} returns HTTP 200 and correct user attributes.
        """
        user_id = 1
        response = api_client.get(f"/users/{user_id}")
        assert_status_code(response, 200)

        user = response.json()
        assert user["id"] == user_id
        assert "name" in user
        assert "email" in user
        assert "role" in user
        assert "created_at" in user
        assert response.headers.get("X-Resource-ID") == str(user_id)

    @pytest.mark.negative
    def test_get_user_by_invalid_id_returns_404(self, api_client: APIClient):
        """
        Verify GET /users/{user_id} returns HTTP 404 for non-existent user ID.
        """
        non_existent_id = 99999
        response = api_client.get(f"/users/{non_existent_id}")
        assert_status_code(response, 404)

        body = response.json()
        assert "detail" in body
        assert f"User with ID {non_existent_id} not found" in body["detail"]

    @pytest.mark.negative
    def test_get_user_by_malformed_string_id_returns_422(self, api_client: APIClient):
        """
        Verify GET /users/{user_id} returns HTTP 422 Unprocessable Entity when ID is not an integer.
        """
        response = api_client.get("/users/invalid_id_string")
        assert_status_code(response, 422)

        body = response.json()
        assert "detail" in body

