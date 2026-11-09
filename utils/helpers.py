"""
Test helper functions for assertions, schema validation, test data loading, and random data generation.
"""

import json
from pathlib import Path
from typing import Any, Dict, Union
import uuid
import jsonschema
from requests import Response

from config.config import settings
from utils.logger import get_logger

logger = get_logger("Helpers")


def load_json(file_path: Union[str, Path]) -> Any:
    """Load and parse a JSON file."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"JSON file not found at: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_json_schema(instance: Any, schema_source: Union[Dict[str, Any], str, Path]) -> None:
    """
    Validate a JSON payload or response body against a JSON Schema.
    Raises detailed AssertionError if validation fails.
    """
    if isinstance(schema_source, (str, Path)):
        schema = load_json(schema_source)
    else:
        schema = schema_source

    try:
        jsonschema.validate(instance=instance, schema=schema)
        logger.debug("JSON Schema validation succeeded.")
    except jsonschema.exceptions.ValidationError as err:
        err_msg = (
            f"JSON Schema Validation Failed!\n"
            f"- Error Message: {err.message}\n"
            f"- Failed Element Path: {' -> '.join(str(p) for p in err.absolute_path)}\n"
            f"- Schema Validator: {err.validator} = {err.validator_value}"
        )
        logger.error(err_msg)
        raise AssertionError(err_msg) from err


def generate_random_email(prefix: str = "qa_user", domain: str = "example.com") -> str:
    """Generate a unique email address to avoid collision in test runs."""
    unique_suffix = uuid.uuid4().hex[:8]
    return f"{prefix}_{unique_suffix}@{domain}"


def generate_random_user(
    name: str = "Automated Test User",
    role: str = "tester",
    status: str = "active",
    age: int = 28
) -> Dict[str, Any]:
    """Generate a valid user dictionary with unique email."""
    return {
        "name": name,
        "email": generate_random_email(),
        "role": role,
        "status": status,
        "age": age
    }


def assert_status_code(response: Response, expected_status: int) -> None:
    """
    Assert response status code with detailed diagnostic failure message.
    """
    if response.status_code != expected_status:
        try:
            body_preview = response.json()
        except Exception:
            body_preview = response.text[:300]
        msg = (
            f"Status Code Mismatch: Expected {expected_status}, but got {response.status_code}.\n"
            f"URL: {response.request.method} {response.url}\n"
            f"Response Body: {body_preview}"
        )
        logger.error(msg)
        assert response.status_code == expected_status, msg


def assert_response_time(response: Response, max_ms: float = settings.MAX_RESPONSE_TIME_MS) -> None:
    """
    Assert that the response time meets the performance SLA.
    """
    elapsed_ms = getattr(response, "elapsed_ms", response.elapsed.total_seconds() * 1000)
    assert elapsed_ms <= max_ms, (
        f"Performance SLA Violated: Response time {elapsed_ms:.2f}ms exceeded "
        f"maximum threshold of {max_ms:.2f}ms for {response.request.method} {response.url}"
    )

