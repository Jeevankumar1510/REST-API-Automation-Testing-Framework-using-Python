"""
API routes for project management, specification parsing, test case review, and ZIP downloads.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from platform_core.database import get_db
from platform_core.models import Endpoint, Project, TestCase
from platform_core.schemas import ProjectCreate, ProjectUpdate
from platform_core.services.generator_service import GeneratorService
from platform_core.services.parser_service import ParserService
from platform_core.services.project_service import ProjectService

router = APIRouter(prefix="/api/platform/projects", tags=["Automation Projects"])


@router.get("", summary="List All Automation Projects")
def list_projects(db: Session = Depends(get_db)):
    """Retrieve all automation projects, ensuring defaults are seeded on serverless/cold starts."""
    if db.query(Project).count() == 0:
        ProjectService.seed_default_projects_if_empty(db)
    projects = db.query(Project).order_by(Project.id.asc()).all()
    return [p.to_dict() for p in projects]


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create New Automation Project")
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    """Creates a new automation project record."""
    existing = db.query(Project).filter(Project.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Project with name '{payload.name}' already exists.")

    project = Project(
        name=payload.name,
        description=payload.description or "",
        app_type=payload.app_type,
        base_url=payload.base_url.rstrip("/"),
        language=payload.language,
        framework=payload.framework,
        auth_type=payload.auth_type,
        auth_token=payload.auth_token
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project.to_dict()


@router.get("/{project_id}", summary="Get Project Details")
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get project details including its endpoints and test cases."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found.")

    data = project.to_dict()
    data["endpoints"] = [ep.to_dict() for ep in project.endpoints]
    data["test_cases"] = [tc.to_dict() for tc in project.test_cases]
    return data


@router.put("/{project_id}", summary="Update Project")
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    """Update project configuration."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    for field, val in payload.model_dump(exclude_unset=True).items():
        if val is not None:
            setattr(project, field, val)

    db.commit()
    db.refresh(project)
    return project.to_dict()


@router.delete("/{project_id}", summary="Delete Project")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Deletes an automation project and associated tests."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    db.delete(project)
    db.commit()
    return {"message": f"Project '{project.name}' deleted successfully."}


@router.post("/parse-spec", summary="Parse OpenAPI or Postman Spec for Wizard Review")
async def parse_specification(
    spec_type: str = Form(..., description="openapi, postman, or url"),
    base_url: Optional[str] = Form(None),
    raw_content: Optional[str] = Form(None),
    spec_file: Optional[UploadFile] = File(None)
):
    """
    Parses OpenAPI (JSON/YAML) or Postman Collection files/strings.
    Generates preview endpoints and suggested test cases before final project approval.
    """
    content = ""
    if spec_file:
        file_bytes = await spec_file.read()
        content = file_bytes.decode("utf-8", errors="ignore")
    elif raw_content:
        content = raw_content
    elif spec_type == "url" and base_url:
        meta, endpoints = await ParserService.auto_discover_from_base_url(base_url)
        suggested_tests = GeneratorService.generate_test_cases(endpoints)
        return {"meta": meta, "endpoints": endpoints, "suggested_tests": suggested_tests}
    else:
        raise HTTPException(status_code=400, detail="Either spec_file or raw_content must be provided.")

    try:
        if spec_type in ["openapi", "swagger"]:
            meta, endpoints = ParserService.parse_openapi(content)
        elif spec_type == "postman":
            collection_dict = json.loads(content)
            meta, endpoints = ParserService.parse_postman_collection(collection_dict)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported spec_type: '{spec_type}'")

        if base_url:
            meta["base_url"] = base_url.rstrip("/")

        suggested_tests = GeneratorService.generate_test_cases(endpoints)
        return {
            "meta": meta,
            "endpoints": endpoints,
            "suggested_tests": suggested_tests
        }
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Failed to parse specification: {str(exc)}")


@router.post("/{project_id}/save-wizard-data", summary="Save Approved Endpoints and Test Cases")
def save_wizard_data(
    project_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Saves reviewed and approved endpoints and test cases for a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    endpoints_data = payload.get("endpoints", [])
    tests_data = payload.get("test_cases", [])

    # Clear previous endpoints and test cases if re-configuring
    db.query(TestCase).filter(TestCase.project_id == project_id).delete()
    db.query(Endpoint).filter(Endpoint.project_id == project_id).delete()

    # Save endpoints
    for ep in endpoints_data:
        db.add(Endpoint(
            project_id=project_id,
            path=ep.get("path", "/"),
            method=ep.get("method", "GET").upper(),
            summary=ep.get("summary", ""),
            description=ep.get("description", ""),
            parameters=json.dumps(ep.get("parameters", [])),
            request_body=json.dumps(ep.get("request_body")) if ep.get("request_body") else None,
            expected_status=ep.get("expected_status", 200),
            auth_required=ep.get("auth_required", False)
        ))

    # Save test cases
    for tc in tests_data:
        db.add(TestCase(
            project_id=project_id,
            name=tc.get("name", "test_generated"),
            category=tc.get("category", "functional"),
            description=tc.get("description", ""),
            http_method=tc.get("http_method", "GET").upper(),
            url_path=tc.get("url_path", "/"),
            headers=json.dumps(tc.get("headers", {})),
            params=json.dumps(tc.get("params", {})),
            payload=json.dumps(tc.get("payload")) if tc.get("payload") else None,
            expected_status=tc.get("expected_status", 200),
            is_enabled=tc.get("is_enabled", True),
            is_approved=True
        ))

    db.commit()
    return {"message": "Project endpoints and approved test cases saved successfully."}


@router.get("/{project_id}/scaffold-preview", summary="Preview Generated Project Code")
def preview_project_scaffold(project_id: int, db: Session = Depends(get_db)):
    """Generates and returns in-memory preview of all project files without downloading."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    test_cases = [tc.to_dict() for tc in project.test_cases]
    slug = GeneratorService.slugify(project.name)
    temp_dir = Path("generated_projects") / slug

    files = GeneratorService.generate_project_scaffold(
        project_name=project.name,
        base_url=project.base_url,
        test_cases=test_cases,
        output_dir=temp_dir
    )
    return {"project_name": project.name, "files": files}


@router.get("/{project_id}/download-zip", summary="Download Automation Project as ZIP")
def download_project_zip(project_id: int, db: Session = Depends(get_db)):
    """Builds and packages the complete Python automation suite as a downloadable ZIP file."""
    try:
        zip_path = ProjectService.export_project_zip(db, project_id)
        if not zip_path.exists():
            raise HTTPException(status_code=500, detail="Could not create project zip archive.")

        return FileResponse(
            path=str(zip_path),
            filename=zip_path.name,
            media_type="application/zip"
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate project zip: {str(exc)}")

