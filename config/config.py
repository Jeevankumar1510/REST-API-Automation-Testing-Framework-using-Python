"""
Centralized Configuration Module for API Automation Testing Framework.
Supports environment-based configuration, default thresholds, and file paths.
"""

import os
from pathlib import Path


# Project Root Directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# File and Directory Paths
REPORTS_DIR = PROJECT_ROOT / "reports"
SCHEMAS_DIR = PROJECT_ROOT / "schemas"
TEST_DATA_DIR = PROJECT_ROOT / "test_data"

USER_SCHEMA_PATH = SCHEMAS_DIR / "user_schema.json"
USERS_TEST_DATA_PATH = TEST_DATA_DIR / "users.json"
LOG_FILE_PATH = REPORTS_DIR / "execution.log"

# Ensure reports directory exists
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class Config:
    """Environment-driven configuration values."""

    # Server & API Host
    HOST: str = os.getenv("API_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("API_PORT", "8000"))
    BASE_URL: str = os.getenv("API_BASE_URL", f"http://{HOST}:{PORT}")

    # Request execution timeouts
    DEFAULT_TIMEOUT: float = float(os.getenv("API_TIMEOUT", "10.0"))

    # Performance / Response Time SLA (milliseconds)
    MAX_RESPONSE_TIME_MS: float = float(os.getenv("MAX_RESPONSE_TIME_MS", "1500.0"))

    # Test Credentials
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin@example.com")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "AdminPass123!")

    TEST_USER_USERNAME: str = os.getenv("TEST_USER_USERNAME", "testuser@example.com")
    TEST_USER_PASSWORD: str = os.getenv("TEST_USER_PASSWORD", "SecretPass123!")

    QA_USERNAME: str = os.getenv("QA_USERNAME", "qa_engineer")
    QA_PASSWORD: str = os.getenv("QA_PASSWORD", "Testing123!")

    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "super-secret-jwt-key-for-api-automation-testing")
    JWT_ALGORITHM: str = "HS256"


# Singleton configuration instance
settings = Config()

