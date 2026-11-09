"""
In-memory database simulation for the FastAPI application.
Provides thread-safe CRUD operations, seed data, and credential management.
"""

from copy import deepcopy
from datetime import datetime, timezone
import threading
from typing import Any, Dict, List, Optional, Tuple


class Database:
    """Thread-safe in-memory database for users and credentials."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._id_counter = 5
        self._users: Dict[int, Dict[str, Any]] = {}
        self._auth_users: Dict[str, str] = {
            "admin@example.com": "AdminPass123!",
            "testuser@example.com": "SecretPass123!",
            "qa_engineer": "Testing123!"
        }
        self.reset_to_seed_data()

    def reset_to_seed_data(self) -> None:
        """Reset the database to initial seed data."""
        with self._lock:
            self._users = {
                1: {
                    "id": 1,
                    "name": "Alice Johnson",
                    "email": "alice@example.com",
                    "role": "admin",
                    "status": "active",
                    "age": 28,
                    "created_at": "2026-01-15T10:00:00Z"
                },
                2: {
                    "id": 2,
                    "name": "Bob Smith",
                    "email": "bob@example.com",
                    "role": "tester",
                    "status": "active",
                    "age": 32,
                    "created_at": "2026-01-16T11:30:00Z"
                },
                3: {
                    "id": 3,
                    "name": "Charlie Brown",
                    "email": "charlie@example.com",
                    "role": "developer",
                    "status": "inactive",
                    "age": 24,
                    "created_at": "2026-01-17T09:15:00Z"
                },
                4: {
                    "id": 4,
                    "name": "Diana Prince",
                    "email": "diana@example.com",
                    "role": "tester",
                    "status": "active",
                    "age": 29,
                    "created_at": "2026-01-18T14:45:00Z"
                },
                5: {
                    "id": 5,
                    "name": "Evan Wright",
                    "email": "evan@example.com",
                    "role": "guest",
                    "status": "active",
                    "age": 22,
                    "created_at": "2026-01-19T16:20:00Z"
                }
            }
            self._id_counter = 5

    def get_all(
        self,
        page: int = 1,
        limit: int = 10,
        role: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Retrieve users with pagination and filtering."""
        with self._lock:
            results = list(self._users.values())

            if role:
                results = [u for u in results if u["role"].lower() == role.lower()]

            if status:
                results = [u for u in results if u["status"].lower() == status.lower()]

            if search:
                term = search.lower()
                results = [
                    u for u in results
                    if term in u["name"].lower() or term in u["email"].lower()
                ]

            total = len(results)
            start = (page - 1) * limit
            end = start + limit
            paginated_results = results[start:end]

            return deepcopy(paginated_results), total

    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a user by their unique ID."""
        with self._lock:
            user = self._users.get(user_id)
            return deepcopy(user) if user else None

    def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """Check if an email already belongs to an existing user."""
        email_clean = email.strip().lower()
        with self._lock:
            for uid, user in self._users.items():
                if exclude_id is not None and uid == exclude_id:
                    continue
                if user["email"].strip().lower() == email_clean:
                    return True
            return False

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create and store a new user."""
        with self._lock:
            self._id_counter += 1
            new_id = self._id_counter
            now_iso = datetime.now(timezone.utc).isoformat()
            new_user = {
                "id": new_id,
                "name": data["name"],
                "email": data["email"].strip().lower(),
                "role": data["role"].lower(),
                "status": data.get("status", "active").lower(),
                "age": data["age"],
                "created_at": now_iso
            }
            self._users[new_id] = new_user
            return deepcopy(new_user)

    def update(self, user_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fully update an existing user."""
        with self._lock:
            if user_id not in self._users:
                return None
            existing = self._users[user_id]
            updated_user = {
                "id": user_id,
                "name": data["name"],
                "email": data["email"].strip().lower(),
                "role": data["role"].lower(),
                "status": data["status"].lower(),
                "age": data["age"],
                "created_at": existing["created_at"]
            }
            self._users[user_id] = updated_user
            return deepcopy(updated_user)

    def patch(self, user_id: int, partial_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Partially update an existing user."""
        with self._lock:
            if user_id not in self._users:
                return None
            user = self._users[user_id]
            for key, val in partial_data.items():
                if val is not None and key in user and key != "id" and key != "created_at":
                    if isinstance(val, str) and key in ["role", "status", "email"]:
                        user[key] = val.strip().lower()
                    else:
                        user[key] = val
            return deepcopy(user)

    def delete(self, user_id: int) -> bool:
        """Delete a user by ID."""
        with self._lock:
            if user_id in self._users:
                del self._users[user_id]
                return True
            return False

    def verify_credentials(self, username: str, password: str) -> bool:
        """Validate login credentials."""
        with self._lock:
            expected_pass = self._auth_users.get(username)
            if expected_pass and expected_pass == password:
                return True
            # Also check if username matches any user email in database
            for user in self._users.values():
                if user["email"] == username and password == "SecretPass123!":
                    return True
            return False


# Singleton instance shared across application
db = Database()

