"""
Automated Test Suite for Response Validation.
Validates JSON structures, JSON Schema contracts, strict Python data types,
mandatory field presence, and response time SLA thresholds.
"""

from typing import Any, Dict
import pytest
from config.config import settings
from utils.api_client import APIClient
from utils.helpers import assert_response_time, assert_status_code, validate_json_schema


@pytest.mark.schema
@pytest.mark.regression
class TestResponseValidation:
    """Test suite for contract, schema, and performance SLA validation."""

    @pytest.mark.smoke
    def test_validate_single_user_json_schema(
        self,
        api_client: APIClient,
        user_schema: Dict[str, Any]
    ):
        """
        Validate that GET /users/{user_id} strictly conforms to the JSON Schema contract.
        """
        response = api_client.get("/users/1")
        assert_status_code(response, 200)

        user_data = response.json()
        validate_json_schema(user_data, user_schema)

    def test_validate_user_list_json_schema(
        self,
        api_client: APIClient,
        user_schema: Dict[str, Any]
    ):
        """
        Validate that GET /users paginated response conforms to the User List JSON Schema contract.
        """
        response = api_client.get("/users")
        assert_status_code(response, 200)

        list_data = response.json()

        # Construct self-contained schema for user_list using root definitions
        list_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "definitions": user_schema["definitions"],
            "$ref": "#/definitions/user_list"
        }
        validate_json_schema(list_data, list_schema)

    def test_validate_user_response_data_types(self, api_client: APIClient):
        """
        Verify strict Python data types of each key in the user response body.
        """
        response = api_client.get("/users/1")
        assert_status_code(response, 200)

        user = response.json()
        assert isinstance(user["id"], int), "'id' must be an integer"
        assert isinstance(user["name"], str), "'name' must be a string"
        assert isinstance(user["email"], str), "'email' must be a string"
        assert isinstance(user["role"], str), "'role' must be a string"
        assert isinstance(user["status"], str), "'status' must be a string"
        assert isinstance(user["age"], int), "'age' must be an integer"
        assert isinstance(user["created_at"], str), "'created_at' must be a string"

    def test_validate_mandatory_fields_presence(self, api_client: APIClient):
        """
        Verify all required fields exist and are neither None nor empty.
        """
        response = api_client.get("/users/1")
        assert_status_code(response, 200)

        user = response.json()
        required_keys = ["id", "name", "email", "role", "status", "age", "created_at"]
        for key in required_keys:
            assert key in user, f"Mandatory key '{key}' is missing from user response"
            assert user[key] is not None, f"Mandatory key '{key}' should not be None"
            if isinstance(user[key], str):
                assert len(user[key].strip()) > 0, f"Mandatory string key '{key}' should not be empty"

    @pytest.mark.performance
    def test_api_response_time_sla_get_users(self, api_client: APIClient):
        """
        Verify GET /users response time is within the defined SLA threshold (< 1500ms).
        """
        response = api_client.get("/users")
        assert_status_code(response, 200)
        assert_response_time(response, max_ms=settings.MAX_RESPONSE_TIME_MS)

    @pytest.mark.performance
    def test_api_response_time_sla_get_single_user(self, api_client: APIClient):
        """
        Verify GET /users/{user_id} response time is within the defined SLA threshold (< 1500ms).
        """
        response = api_client.get("/users/1")
        assert_status_code(response, 200)
        assert_response_time(response, max_ms=settings.MAX_RESPONSE_TIME_MS)
