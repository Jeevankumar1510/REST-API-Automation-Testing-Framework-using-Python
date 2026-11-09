"""
API routes for secure GitHub Actions integration and live CI/CD run synchronization.
"""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from platform_core.database import get_db
from platform_core.models import GitHubConfig
from platform_core.schemas import GitHubConfigCreate
from platform_core.services.github_service import GitHubService

router = APIRouter(prefix="/api/platform/github", tags=["GitHub Integration"])


@router.get("/config", summary="Get GitHub Configuration")
def get_github_config(db: Session = Depends(get_db)):
    """Returns stored GitHub repository connection info with token masked."""
    config = db.query(GitHubConfig).first()
    if not config:
        return {
            "is_connected": False,
            "repo_owner": "",
            "repo_name": "",
            "branch": "main",
            "workflow_filename": "tests.yml",
            "has_token": False
        }
    return config.to_dict(mask_token=True)


@router.post("/config", summary="Connect and Save GitHub Repository")
async def save_github_config(payload: GitHubConfigCreate, db: Session = Depends(get_db)):
    """Verifies access to GitHub repository and stores connection settings."""
    is_valid, message = await GitHubService.verify_connection(
        owner=payload.repo_owner,
        repo=payload.repo_name,
        token=payload.access_token
    )

    config = db.query(GitHubConfig).first()
    if not config:
        config = GitHubConfig(
            repo_owner=payload.repo_owner,
            repo_name=payload.repo_name,
            branch=payload.branch,
            workflow_filename=payload.workflow_filename,
            access_token=payload.access_token,
            is_connected=is_valid,
            last_synced_at=datetime.now(timezone.utc) if is_valid else None
        )
        db.add(config)
    else:
        config.repo_owner = payload.repo_owner
        config.repo_name = payload.repo_name
        config.branch = payload.branch
        config.workflow_filename = payload.workflow_filename
        if payload.access_token:
            config.access_token = payload.access_token
        config.is_connected = is_valid
        if is_valid:
            config.last_synced_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(config)

    res = config.to_dict(mask_token=True)
    res["verification_message"] = message
    return res


@router.get("/runs", summary="Live Fetch Real GitHub Actions Runs")
async def fetch_github_actions_runs(
    limit: int = Query(10, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """
    Live queries the GitHub Actions API for real workflow runs if configured,
    or returns local execution pipeline runs if GitHub is not yet connected.
    """
    config = db.query(GitHubConfig).first()
    if config and config.repo_owner and config.repo_name:
        runs = await GitHubService.get_workflow_runs(
            owner=config.repo_owner,
            repo=config.repo_name,
            token=config.access_token,
            branch=config.branch,
            limit=limit
        )
        if runs:
            return {"source": "github_actions", "runs": runs}

    # Fallback to local pipeline runs
    from platform_core.models import PipelineRun
    local_runs = db.query(PipelineRun).order_by(PipelineRun.id.desc()).limit(limit).all()
    return {
        "source": "local_pipeline",
        "runs": [
            {
                "id": r.run_id or r.id,
                "name": r.workflow_name,
                "event": r.trigger_event,
                "status": r.status,
                "conclusion": r.conclusion,
                "branch": r.branch,
                "commit_sha": r.commit_hash[:7],
                "commit_message": r.commit_message,
                "created_at": r.started_at.isoformat() if r.started_at else None,
                "html_url": "#"
            }
            for r in local_runs
        ]
    }


@router.post("/trigger", summary="Trigger GitHub Actions Workflow Run")
async def trigger_github_workflow(db: Session = Depends(get_db)):
    """Dispatches a manual workflow run on GitHub Actions."""
    config = db.query(GitHubConfig).first()
    if not config or not config.access_token:
        raise HTTPException(
            status_code=400,
            detail="GitHub connection or Personal Access Token not configured."
        )

    success, message = await GitHubService.trigger_workflow(
        owner=config.repo_owner,
        repo=config.repo_name,
        workflow_id=config.workflow_filename,
        branch=config.branch,
        token=config.access_token
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"message": message, "status": "triggered"}

