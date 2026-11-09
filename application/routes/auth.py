"""
Authentication routes and JWT security dependencies.
Handles login, token generation, and authorization verification.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from application.database import db
from application.models import LoginRequest, TokenResponse


# Authentication configuration constants
SECRET_KEY = "super-secret-jwt-key-for-api-automation-testing"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter(tags=["Authentication"])
security = HTTPBearer(auto_error=False)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generate a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI security dependency to validate JWT Bearer token.
    Raises 401 Unauthorized for missing or invalid tokens.
    """
    auth_header = request.headers.get("Authorization")

    # Check if Authorization header is missing
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Check scheme prefix
    if not auth_header.strip().lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Expected Bearer token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token payload",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User Authentication",
    description="Authenticates credentials and returns a signed JWT Bearer token."
)
def login(credentials: LoginRequest):
    """Authenticate user with username/email and password."""
    is_valid = db.verify_credentials(credentials.username, credentials.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token({"sub": credentials.username}, expires_delta=expires)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get(
    "/auth/verify",
    status_code=status.HTTP_200_OK,
    summary="Verify Bearer Token",
    description="Validates that the provided Bearer token is authentic and active."
)
def verify_token(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Protected endpoint to check token validity."""
    return {
        "status": "authenticated",
        "user": current_user.get("sub")
    }


@router.post(
    "/reset-db",
    status_code=status.HTTP_200_OK,
    summary="Reset Test Database",
    description="Resets the in-memory database to seed state (used by test harness)."
)
def reset_database():
    """Reset database state."""
    db.reset_to_seed_data()
    return {"message": "Database reset to initial seed data successfully"}
