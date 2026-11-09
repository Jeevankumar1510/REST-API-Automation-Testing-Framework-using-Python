"""
Project lifecycle management and ZIP export service.
Provides project initialization, seeding of default projects, and project packaging.
"""

from copy import deepcopy
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import shutil
import zipfile
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from platform_core.models import Endpoint, Project, TestCase, TestExecution
from platform_core.services.generator_service import GeneratorService


class ProjectService:
    """Manages automation projects, database seeding, and ZIP exports."""

    @staticmethod
    def seed_default_projects_if_empty(db: Session) -> None:
        """Seed initial realistic projects so the dashboard is immediately populated."""
        if db.query(Project).count() > 0:
            return

        # 1. User Management REST API (Directly points to our built-in FastAPI target!)
        user_mgmt = Project(
            name="User Management REST API",
            description="Core user microservice featuring JWT authentication, role management, and CRUD endpoints.",
            app_type="user_management",
            base_url="http://127.0.0.1:8000",
            language="Python",
            framework="Pytest + Requests",
            auth_type="bearer",
            auth_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlckBleGFtcGxlLmNvbSIsImV4cCI6MTc5NDIxODAwMH0.sample_signature_jwt",
            status="active"
        )
        db.add(user_mgmt)
        db.flush()

        # Seed Endpoints for User Management
        user_endpoints = [
            {"path": "/users", "method": "GET", "summary": "Retrieve All Users", "expected_status": 200, "auth_required": False},
            {"path": "/users/{user_id}", "method": "GET", "summary": "Retrieve User by ID", "expected_status": 200, "auth_required": False},
            {"path": "/users", "method": "POST", "summary": "Create User", "expected_status": 201, "auth_required": True, "request_body": {"name": "Alex Mercer", "email": "alex.mercer@example.com", "role": "tester", "status": "active", "age": 29}},
            {"path": "/users/{user_id}", "method": "PUT", "summary": "Full User Update", "expected_status": 200, "auth_required": True, "request_body": {"name": "Alex Updated", "email": "alex.upd@example.com", "role": "developer", "status": "active", "age": 30}},
            {"path": "/users/{user_id}", "method": "PATCH", "summary": "Partial User Update", "expected_status": 200, "auth_required": True, "request_body": {"role": "admin"}},
            {"path": "/users/{user_id}", "method": "DELETE", "summary": "Delete User", "expected_status": 200, "auth_required": True},
            {"path": "/login", "method": "POST", "summary": "User Authentication", "expected_status": 200, "auth_required": False, "request_body": {"username": "testuser@example.com", "password": "SecretPass123!"}},
            {"path": "/health", "method": "GET", "summary": "Service Healthcheck", "expected_status": 200, "auth_required": False}
        ]

        ep_models = []
        for ep in user_endpoints:
            ep_model = Endpoint(
                project_id=user_mgmt.id,
                path=ep["path"],
                method=ep["method"],
                summary=ep["summary"],
                expected_status=ep["expected_status"],
                auth_required=ep["auth_required"],
                request_body=json.dumps(ep.get("request_body")) if ep.get("request_body") else None
            )
            db.add(ep_model)
            ep_models.append(ep)

        # Generate test cases
        tests = GeneratorService.generate_test_cases(ep_models, auth_type="bearer", auth_token=user_mgmt.auth_token)
        for t in tests:
            tc = TestCase(
                project_id=user_mgmt.id,
                name=t["name"],
                category=t["category"],
                description=t["description"],
                http_method=t["http_method"],
                url_path=t["url_path"],
                headers=json.dumps(t.get("headers", {})),
                params=json.dumps(t.get("params", {})),
                payload=json.dumps(t.get("payload")) if t.get("payload") else None,
                expected_status=t["expected_status"],
                is_enabled=True,
                is_approved=True
            )
            db.add(tc)

        # Seed initial execution record
        exec_record = TestExecution(
            project_id=user_mgmt.id,
            execution_type="all",
            total_tests=len(tests),
            passed_tests=len(tests),
            failed_tests=0,
            skipped_tests=0,
            duration_seconds=2.45,
            status="passed",
            output_logs="Initial baseline execution verified 100% passing tests.",
            completed_at=datetime.now(timezone.utc)
        )
        db.add(exec_record)

        # 2. E-Commerce Store API
        ecom = Project(
            name="E-Commerce Store API",
            description="Catalog, Shopping Cart, and Checkout service automation for online retail platform.",
            app_type="ecommerce",
            base_url="https://api.escuelajs.co/api/v1",
            language="Python",
            framework="Pytest + Requests",
            auth_type="bearer",
            status="active"
        )
        db.add(ecom)
        db.flush()

        ecom_endpoints = [
            {"path": "/products", "method": "GET", "summary": "Get Products Catalog", "expected_status": 200, "auth_required": False},
            {"path": "/products/{id}", "method": "GET", "summary": "Get Product by ID", "expected_status": 200, "auth_required": False},
            {"path": "/categories", "method": "GET", "summary": "List Categories", "expected_status": 200, "auth_required": False},
            {"path": "/users", "method": "GET", "summary": "List Customer Accounts", "expected_status": 200, "auth_required": False}
        ]
        for ep in ecom_endpoints:
            db.add(Endpoint(
                project_id=ecom.id,
                path=ep["path"],
                method=ep["method"],
                summary=ep["summary"],
                expected_status=ep["expected_status"],
                auth_required=ep["auth_required"]
            ))

        ecom_tests = GeneratorService.generate_test_cases(ecom_endpoints, auth_type="none")
        for t in ecom_tests:
            db.add(TestCase(
                project_id=ecom.id,
                name=t["name"],
                category=t["category"],
                description=t["description"],
                http_method=t["http_method"],
                url_path=t["url_path"],
                headers=json.dumps(t.get("headers", {})),
                params=json.dumps(t.get("params", {})),
                payload=json.dumps(t.get("payload")) if t.get("payload") else None,
                expected_status=t["expected_status"],
                is_enabled=True,
                is_approved=True
            ))

        db.commit()

    @staticmethod
    def export_project_zip(db: Session, project_id: int) -> Path:
        """
        Builds the standalone Python test project on disk and packages it into a downloadable .zip file.
        Returns the absolute path to the generated zip archive.
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project with ID {project_id} not found.")

        test_cases = [tc.to_dict() for tc in project.test_cases]
        slug = GeneratorService.slugify(project.name)

        target_dir = Path("generated_projects") / slug
        target_dir.mkdir(parents=True, exist_ok=True)

        # Generate files
        GeneratorService.generate_project_scaffold(
            project_name=project.name,
            base_url=project.base_url,
            test_cases=test_cases,
            output_dir=target_dir
        )

        # Package into ZIP archive
        zip_path = Path("generated_projects") / f"{slug}_automation_suite.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in target_dir.walk() if hasattr(target_dir, "walk") else shutil.os.walk(target_dir):
                for f in files:
                    file_full = Path(root) / f
                    rel_path = file_full.relative_to(target_dir)
                    zf.write(file_full, arcname=rel_path)

        return zip_path

