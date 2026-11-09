"""
API route controllers for 3D CI/CD pipeline runs and stage status monitoring.
"""

from datetime import datetime, timezone
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from platform_core.database import get_db
from platform_core.models import PipelineRun, Project, TestExecution
from platform_core.schemas import PipelineTriggerRequest

router = APIRouter(prefix="/api/platform/pipeline", tags=["3D CI/CD Pipeline"])


DEFAULT_11_STAGES = [
    {"id": 1, "name": "Developer Code", "status": "success", "duration": "0.1s", "details": "Code pushed to branch main", "metrics": {"files_changed": 4, "insertions": 120}},
    {"id": 2, "name": "Git Repository", "status": "success", "duration": "0.2s", "details": "Commit 392961f verified on origin/main", "metrics": {"branch": "main", "author": "QA Engineer"}},
    {"id": 3, "name": "GitHub Webhook", "status": "success", "duration": "0.1s", "details": "Payload delivered with signature 200 OK", "metrics": {"event": "push", "status": "delivered"}},
    {"id": 4, "name": "CI/CD Trigger", "status": "success", "duration": "0.1s", "details": "Workflow job scheduled on runner ubuntu-latest", "metrics": {"runner": "ubuntu-latest", "job_id": 41209}},
    {"id": 5, "name": "Dependency Installation", "status": "success", "duration": "1.4s", "details": "Installed requirements.txt (fastapi, pytest, requests, jsonschema)", "metrics": {"packages": 9, "cache": "hit"}},
    {"id": 6, "name": "Code Quality Checks", "status": "success", "duration": "0.6s", "details": "PEP 8 syntax validation & Pydantic schema validation clean", "metrics": {"linter": "flake8", "violations": 0}},
    {"id": 7, "name": "Pytest Execution", "status": "success", "duration": "2.55s", "details": "Pytest 8.3 executed 66 test items", "metrics": {"total": 66, "passed": 66, "failed": 0, "skipped": 0}},
    {"id": 8, "name": "API Test Execution", "status": "success", "duration": "2.55s", "details": "Requests session completed CRUD & Auth suites", "metrics": {"avg_latency_ms": 14.8, "endpoints": 7}},
    {"id": 9, "name": "Test Result Validation", "status": "success", "duration": "0.2s", "details": "HTTP status codes, Draft-7 JSON schema & SLA limits verified", "metrics": {"schema_checks": "100%", "sla_violations": 0}},
    {"id": 10, "name": "HTML Report Generation", "status": "success", "duration": "0.3s", "details": "Self-contained HTML test execution dashboard compiled", "metrics": {"report_file": "reports/report.html", "size_kb": 102}},
    {"id": 11, "name": "Deployment / Release Status", "status": "success", "duration": "0.2s", "details": "Pipeline passed all quality gates. Staging deployment ready.", "metrics": {"gate": "APPROVED", "environment": "Staging"}}
]


@router.get("/latest", summary="Get Latest Pipeline Status for 3D Visualizer")
def get_latest_pipeline_status(db: Session = Depends(get_db)):
    """
    Returns current state of all 11 CI/CD stages.
    Used directly by the Three.js 3D pipeline visualizer.
    """
    latest_run = db.query(PipelineRun).order_by(PipelineRun.id.desc()).first()
    if latest_run and latest_run.stages_data:
        stages = json.loads(latest_run.stages_data)
        run_dict = latest_run.to_dict()
        run_dict["stages"] = stages
        return run_dict

    # Return default baseline
    return {
        "id": 1,
        "workflow_name": "API Automation Test Pipeline",
        "run_id": "gh-run-41029",
        "branch": "main",
        "commit_hash": "392961f",
        "commit_message": "feat: complete REST API automation testing framework",
        "trigger_event": "push",
        "status": "completed",
        "conclusion": "success",
        "stages": DEFAULT_11_STAGES,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat()
    }


@router.get("/runs", summary="Get Pipeline Run History")
def get_pipeline_runs(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """Returns recent pipeline runs."""
    runs = db.query(PipelineRun).order_by(PipelineRun.id.desc()).limit(limit).all()
    return [r.to_dict() for r in runs]


@router.post("/simulate", summary="Trigger or Simulate Live Pipeline Execution")
def trigger_pipeline_simulation(payload: PipelineTriggerRequest, db: Session = Depends(get_db)):
    """
    Triggers an execution run and updates all 11 stages with realistic sequential metrics.
    """
    run = PipelineRun(
        project_id=payload.project_id,
        workflow_name="Interactive 3D Pipeline Execution",
        run_id=f"sim-{int(datetime.now().timestamp())}",
        branch=payload.branch or "main",
        commit_hash="a1b2c3d",
        commit_message=f"Pipeline trigger: {payload.trigger_event}",
        trigger_event=payload.trigger_event or "manual",
        status="completed",
        conclusion="success",
        stages_data=json.dumps(DEFAULT_11_STAGES),
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        logs="All 11 pipeline stages executed and verified successfully."
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    res = run.to_dict()
    res["stages"] = DEFAULT_11_STAGES
    return res

