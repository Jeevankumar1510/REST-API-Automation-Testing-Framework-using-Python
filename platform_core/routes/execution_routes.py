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


@router.post("/run", status_code=status.HTTP_200_OK, summary="Execute Test Suite")
def run_test_suite(payload: ExecutionRequest, db: Session = Depends(get_db)):
    """
    Executes automated test cases against target API.
    Supports execution types: all, functional, negative, auth, selected.
    """
    try:
        execution = RunnerService.execute_test_suite(
            db=db,
            project_id=payload.project_id,
            execution_type=payload.execution_type,
            test_case_ids=payload.test_case_ids
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

