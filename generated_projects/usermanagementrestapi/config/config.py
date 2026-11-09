"""
Centralized Configuration for User Management REST API.
"""
import os

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
DEFAULT_TIMEOUT = float(os.getenv("API_TIMEOUT", "10.0"))
MAX_RESPONSE_TIME_MS = float(os.getenv("MAX_RESPONSE_TIME_MS", "1500.0"))
