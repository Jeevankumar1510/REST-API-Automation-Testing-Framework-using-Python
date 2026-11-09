"""
User management API routes for CRUD operations.
Supports filtering, pagination, custom response headers, and token authentication.
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status

from application.database import db
from application.models import (
    MessageResponse,
    UserCreate,
    UserListResponse,
    UserPatch,
    UserResponse,
    UserUpdate
)
from application.routes.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve All Users",
    description="Retrieves a paginated list of users with optional filtering by role, status, or search term."
)
def get_users(
    response: Response,
    page: int = Query(1, ge=1, description="Page number, starting at 1"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    role: Optional[str] = Query(None, description="Filter by role (admin, tester, developer, guest)"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (active, inactive)"),
    search: Optional[str] = Query(None, description="Search by name or email")
):
    """Retrieve all users with optional filtering and pagination."""
    users, total = db.get_all(
        page=page,
        limit=limit,
        role=role,
        status=status_filter,
        search=search
    )

    response.headers["X-Total-Count"] = str(total)
    response.headers["X-Page-Number"] = str(page)
    response.headers["X-Page-Limit"] = str(limit)

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": users
    }


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve Specific User",
    description="Retrieves full profile details for a given user ID."
)
def get_user_by_id(
    response: Response,
    user_id: int = Path(..., ge=1, description="Unique ID of user")
):
    """Retrieve user details by user ID."""
    user = db.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    response.headers["X-Resource-ID"] = str(user_id)
    return user


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create User",
    description="Creates a new user account. Requires Bearer authentication."
)
def create_user(
    payload: UserCreate,
    response: Response,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new user with email uniqueness validation."""
    if db.email_exists(payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{payload.email}' already registered"
        )

    created_user = db.create(payload.model_dump())
    response.headers["Location"] = f"/users/{created_user['id']}"
    return created_user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update User (Full Replace)",
    description="Replaces all fields for an existing user. Requires Bearer authentication."
)
def update_user(
    payload: UserUpdate,
    user_id: int = Path(..., ge=1, description="Unique ID of user"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Fully update an existing user."""
    existing = db.get_by_id(user_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    if db.email_exists(payload.email, exclude_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{payload.email}' is already in use by another user"
        )

    updated_user = db.update(user_id, payload.model_dump())
    return updated_user


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Partially Update User",
    description="Updates specific fields of an existing user. Requires Bearer authentication."
)
def patch_user(
    payload: UserPatch,
    user_id: int = Path(..., ge=1, description="Unique ID of user"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Partially update an existing user."""
    existing = db.get_by_id(user_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    patch_data = payload.model_dump(exclude_unset=True)
    # Ensure at least one field is provided
    if not patch_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty patch payload: at least one field must be provided for update"
        )

    if "email" in patch_data and patch_data["email"]:
        if db.email_exists(patch_data["email"], exclude_id=user_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{patch_data['email']}' is already in use by another user"
            )

    updated_user = db.patch(user_id, patch_data)
    return updated_user


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete User",
    description="Permanently removes a user by ID. Requires Bearer authentication."
)
def delete_user(
    user_id: int = Path(..., ge=1, description="Unique ID of user"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a user by ID."""
    success = db.delete(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    return {
        "message": f"User {user_id} deleted successfully",
        "deleted_user_id": user_id
    }

