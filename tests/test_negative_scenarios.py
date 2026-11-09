"""
Automated Test Suite for Negative Scenarios and Robustness.
Validates invalid endpoints (404), invalid HTTP methods (405), incorrect data types (422),
path boundary violations, malformed JSON, and security injection safety.
"""

from typing import Any, Dict
import pytest
from utils.api_client import APIClient
from utils.helpers import assert_status_code, generate_random_user


@pytest.mark.negative
@pytest.mark.regression
class TestNegativeScenarios:
    """Test suite covering edge cases, invalid inputs, and security boundary tests."""

    def test_invalid_api_endpoint_returns_404(self, api_client: APIClient):
        """
        Verify requesting a non-existent API endpoint returns HTTP 404 Not Found.
        """
        response = api_client.get("/api/v1/non_existent_route")
        assert_status_code(response, 404)

    def test_invalid_http_method_returns_405(self, api_client: APIClient):
        """
        Verify executing an unsupported HTTP method on an endpoint returns HTTP 405 Method Not Allowed.
        """
        # POST is not allowed on /users/{user_id}
        response = api_client.post("/users/1", json={"data": "test"})
        assert_status_code(response, 405)

    def test_incorrect_data_types_in_payload(
        self,
        authenticated_client: APIClient,
        test_data: Dict[str, Any]
    ):
        """
        Verify payloads with incorrect data types (e.g. string for integer) return HTTP 422.
        """
        cases = test_data["invalid_users_wrong_types"]
        for case in cases:
            response = authenticated_client.post("/users", json=case["payload"])
            assert response.status_code == case["expected_status"], (
                f"Failed scenario: {case['description']}. Expected {case['expected_status']}, "
                f"got {response.status_code}"
            )

    @pytest.mark.parametrize("invalid_id", [0, -1, -99])
    def test_negative_or_zero_user_id_returns_422(
        self,
        api_client: APIClient,
        invalid_id: int
    ):
        """
        Verify passing zero or negative integers in user_id path parameter returns HTTP 422.
        """
        response = api_client.get(f"/users/{invalid_id}")
        assert_status_code(response, 422)

    def test_sql_injection_payload_handled_safely(
        self,
        authenticated_client: APIClient
    ):
        """
        Verify injecting SQL injection syntax into query parameter or payload is safely processed.
        """
        sql_payload = "' OR 1=1; --"
        response = authenticated_client.get("/users", params={"search": sql_payload})
        assert_status_code(response, 200)

        # Should return normal envelope without crashing
        body = response.json()
        assert isinstance(body["data"], list)

    def test_xss_script_payload_handled_safely(
        self,
        authenticated_client: APIClient
    ):
        """
        Verify injecting XSS HTML/script payload into user name is treated strictly as plain data.
        """
        xss_string = "<script>alert('xss');</script>"
        payload = generate_random_user(name=xss_string)

        response = authenticated_client.post("/users", json=payload)
        assert_status_code(response, 201)

        user_id = response.json()["id"]
        assert response.json()["name"] == xss_string

        # Clean up
        authenticated_client.delete(f"/users/{user_id}")

    def test_malformed_json_body_returns_422(self, authenticated_client: APIClient):
        """
        Verify sending a malformed JSON string payload returns HTTP 422 Unprocessable Entity.
        """
        headers = {"Content-Type": "application/json"}
        malformed_body = '{"name": "Broken JSON", "email": }'

        response = authenticated_client.post("/users", data=malformed_body, headers=headers)
        assert_status_code(response, 422)
