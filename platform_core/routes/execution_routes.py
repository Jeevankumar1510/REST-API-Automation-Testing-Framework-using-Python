"""
API route controllers for test execution, live logs, execution history, and HTML reports.
"""

from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from platform_core.database import get_db
from platform_core.models import TestExecution
from platform_core.schemas import ExecutionRequest
from platform_core.services.runner_service import RunnerService

router = APIRouter(prefix="/api/platform/execution", tags=["Test Execution"])


@router.get("/files", summary="List Available Pytest Test Files")
def list_test_files():
    """Returns all available test files in tests/ directory with descriptions and test counts."""
    return [
        {
            "filename": "all",
            "display_name": "📁 All Test Files (Full Suite - 78 Tests)",
            "tests_count": 78,
            "category": "all",
            "description": "Full end-to-end regression test suite covering all endpoints, negative scenarios, and quality gates."
        },
        {
            "filename": "tests/test_authentication.py",
            "display_name": "📄 test_authentication.py (JWT Authentication & Login - 9 Tests)",
            "tests_count": 9,
            "category": "auth",
            "description": "Validates /login with valid & invalid credentials, JWT token verification, and 401 unauthorized route protections."
        },
        {
            "filename": "tests/test_create_users.py",
            "display_name": "📄 test_create_users.py (POST /users Functional & Validation - 8 Tests)",
            "tests_count": 8,
            "category": "functional",
            "description": "Tests user creation with HTTP 201, duplicate email conflict (409), required fields, email format, and age boundary validation."
        },
        {
            "filename": "tests/test_get_users.py",
            "display_name": "📄 test_get_users.py (GET /users & Query/Pagination - 17 Tests)",
            "tests_count": 17,
            "category": "functional",
            "description": "Validates retrieval of all users, pagination, filtering by role and status, search queries, and single user lookup by ID."
        },
        {
            "filename": "tests/test_update_users.py",
            "display_name": "📄 test_update_users.py (PUT & PATCH User Update Suite - 8 Tests)",
            "tests_count": 8,
            "category": "functional",
            "description": "Tests full updates via PUT, partial field updates via PATCH, empty payload handling, and duplicate email conflicts."
        },
        {
            "filename": "tests/test_delete_users.py",
            "display_name": "📄 test_delete_users.py (DELETE /users/{id} Integrity - 5 Tests)",
            "tests_count": 5,
            "category": "functional",
            "description": "Verifies successful user deletion (200), cascade verification, nonexistent ID handling (404), and unauthenticated rejections."
        },
        {
            "filename": "tests/test_negative_scenarios.py",
            "display_name": "📄 test_negative_scenarios.py (Negative & Security Scenarios - 9 Tests)",
            "tests_count": 9,
            "category": "negative",
            "description": "Validates resilience against 404 routes, 405 methods, malformed JSON, SQL injection vectors, and XSS attack payloads."
        },
        {
            "filename": "tests/test_response_validation.py",
            "display_name": "📄 test_response_validation.py (JSON Schema & Latency SLA - 6 Tests)",
            "tests_count": 6,
            "category": "performance",
            "description": "Enforces JSON schema validation, data type verification, mandatory response keys, and response time SLA compliance."
        },
        {
            "filename": "tests/test_platform_upgrade.py",
            "display_name": "📄 test_platform_upgrade.py (Platform Core & CI/CD Pipeline - 16 Tests)",
            "tests_count": 16,
            "category": "functional",
            "description": "Tests platform dashboard statistics, OpenAPI & Postman collection import parsers, scaffold previews, and 3D CI/CD stages."
        }
    ]


@router.post("/run", status_code=status.HTTP_200_OK, summary="Execute Test Suite")
def run_test_suite(payload: ExecutionRequest, db: Session = Depends(get_db)):
    """
    Executes automated test cases against target API.
    Supports selecting specific test files (e.g. tests/test_authentication.py) or execution types.
    """
    try:
        execution = RunnerService.execute_test_suite(
            db=db,
            project_id=payload.project_id,
            execution_type=payload.execution_type,
            test_file=payload.test_file or "all",
            test_case_ids=payload.test_case_ids,
            custom_file_name=payload.custom_file_name,
            custom_file_content=payload.custom_file_content
        )
        return execution.to_dict()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(exc)}")


@router.get("/history/{project_id}", summary="Get Execution History for Project")
def get_execution_history(
    project_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retrieves past test execution records for a specific project."""
    history = db.query(TestExecution).filter(
        TestExecution.project_id == project_id
    ).order_by(TestExecution.started_at.desc()).limit(limit).all()

    return [h.to_dict() for h in history]


@router.get("/{execution_id}", summary="Get Execution Details & Logs")
def get_execution_details(execution_id: int, db: Session = Depends(get_db)):
    """Retrieves full execution details, logs, and per-test diagnostic results."""
    execution = db.query(TestExecution).filter(TestExecution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution record not found.")

    return execution.to_dict()


@router.get("/{execution_id}/report", response_class=HTMLResponse, summary="View HTML Execution Report")
def view_execution_report(execution_id: int, db: Session = Depends(get_db)):
    """Returns the standalone HTML report for an execution run."""
    execution = db.query(TestExecution).filter(TestExecution.id == execution_id).first()
    if not execution or not execution.report_path:
        raise HTTPException(status_code=404, detail="Report not found for this execution.")

    report_path = Path(execution.report_path)
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="HTML report file missing on disk.")

    with open(report_path, "r", encoding="utf-8") as f:
        html = f.read()

    return HTMLResponse(content=html)

