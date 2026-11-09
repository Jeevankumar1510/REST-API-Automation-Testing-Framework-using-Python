"""
SQLAlchemy ORM models for the Intelligent API Automation Platform.
Stores projects, endpoints, test cases, test executions, pipeline runs, and GitHub credentials.
"""

from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import relationship

from platform_core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Project(Base):
    """Stores metadata and configuration for an automation project."""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    app_type = Column(String(50), default="custom")  # ecommerce, banking, healthcare, user_management, custom
    base_url = Column(String(255), nullable=False)
    language = Column(String(30), default="Python")
    framework = Column(String(50), default="Pytest + Requests")
    auth_type = Column(String(30), default="none")  # none, bearer, basic, api_key
    auth_token = Column(String(500), nullable=True)
    auth_config = Column(Text, nullable=True)  # JSON string for extra auth details
    status = Column(String(30), default="active")  # active, archived
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    endpoints = relationship("Endpoint", back_populates="project", cascade="all, delete-orphan")
    test_cases = relationship("TestCase", back_populates="project", cascade="all, delete-orphan")
    executions = relationship("TestExecution", back_populates="project", cascade="all, delete-orphan")
    pipeline_runs = relationship("PipelineRun", back_populates="project", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        latest_exec = self.executions[-1] if self.executions else None
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description or "",
            "app_type": self.app_type,
            "base_url": self.base_url,
            "language": self.language,
            "framework": self.framework,
            "auth_type": self.auth_type,
            "status": self.status,
            "endpoints_count": len(self.endpoints),
            "test_cases_count": len(self.test_cases),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "latest_execution": latest_exec.to_dict() if latest_exec else None
        }


class Endpoint(Base):
    """Stores API endpoints associated with a project."""
    __tablename__ = "endpoints"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    path = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)  # GET, POST, PUT, PATCH, DELETE
    summary = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    parameters = Column(Text, nullable=True)  # JSON serialized list of params
    request_body = Column(Text, nullable=True)  # JSON template
    expected_status = Column(Integer, default=200)
    auth_required = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)

    # Relationship
    project = relationship("Project", back_populates="endpoints")
    test_cases = relationship("TestCase", back_populates="endpoint")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "path": self.path,
            "method": self.method,
            "summary": self.summary or "",
            "description": self.description or "",
            "parameters": json.loads(self.parameters) if self.parameters else [],
            "request_body": json.loads(self.request_body) if self.request_body else None,
            "expected_status": self.expected_status,
            "auth_required": self.auth_required
        }


class TestCase(Base):
    """Stores generated or customized test cases."""
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    endpoint_id = Column(Integer, ForeignKey("endpoints.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(150), nullable=False)
    category = Column(String(50), default="functional")  # functional, positive, negative, auth, schema, performance
    description = Column(Text, nullable=True)
    http_method = Column(String(10), nullable=False)
    url_path = Column(String(255), nullable=False)
    headers = Column(Text, nullable=True)  # JSON string
    params = Column(Text, nullable=True)  # JSON string
    payload = Column(Text, nullable=True)  # JSON string
    expected_status = Column(Integer, default=200)
    expected_schema = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    project = relationship("Project", back_populates="test_cases")
    endpoint = relationship("Endpoint", back_populates="test_cases")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "endpoint_id": self.endpoint_id,
            "name": self.name,
            "category": self.category,
            "description": self.description or "",
            "http_method": self.http_method,
            "url_path": self.url_path,
            "headers": json.loads(self.headers) if self.headers else {},
            "params": json.loads(self.params) if self.params else {},
            "payload": json.loads(self.payload) if self.payload else None,
            "expected_status": self.expected_status,
            "is_enabled": self.is_enabled,
            "is_approved": self.is_approved
        }


class TestExecution(Base):
    """Audit log and metrics for test execution runs."""
    __tablename__ = "test_executions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    execution_type = Column(String(50), default="all")  # all, functional, negative, auth, smoke, selected
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    skipped_tests = Column(Integer, default=0)
    duration_seconds = Column(Float, default=0.0)
    status = Column(String(30), default="completed")  # running, passed, failed, error
    output_logs = Column(Text, nullable=True)
    report_path = Column(String(255), nullable=True)
    details_json = Column(Text, nullable=True)  # JSON array of test results
    started_at = Column(DateTime, default=utcnow)
    completed_at = Column(DateTime, default=utcnow)

    # Relationship
    project = relationship("Project", back_populates="executions")

    def to_dict(self) -> Dict[str, Any]:
        pass_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0.0
        return {
            "id": self.id,
            "project_id": self.project_id,
            "project_name": self.project.name if self.project else "",
            "execution_type": self.execution_type,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "skipped_tests": self.skipped_tests,
            "pass_rate": round(pass_rate, 1),
            "duration_seconds": round(self.duration_seconds, 2),
            "status": self.status,
            "output_logs": self.output_logs or "",
            "report_path": self.report_path or "",
            "details": json.loads(self.details_json) if self.details_json else [],
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class PipelineRun(Base):
    """Records for 3D CI/CD pipeline runs, synchronized with local execution or GitHub Actions."""
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    workflow_name = Column(String(120), default="API Automation Test Pipeline")
    run_id = Column(String(50), nullable=True)
    branch = Column(String(80), default="main")
    commit_hash = Column(String(40), default="HEAD")
    commit_message = Column(String(255), default="Automated test suite run")
    trigger_event = Column(String(40), default="workflow_dispatch")  # push, pull_request, manual
    status = Column(String(30), default="completed")  # queued, in_progress, completed, failed
    conclusion = Column(String(30), default="success")  # success, failure, cancelled
    stages_data = Column(Text, nullable=True)  # JSON list of stage states
    started_at = Column(DateTime, default=utcnow)
    completed_at = Column(DateTime, default=utcnow)
    logs = Column(Text, nullable=True)

    # Relationship
    project = relationship("Project", back_populates="pipeline_runs")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "workflow_name": self.workflow_name,
            "run_id": self.run_id or str(self.id),
            "branch": self.branch,
            "commit_hash": self.commit_hash[:7] if self.commit_hash else "HEAD",
            "commit_message": self.commit_message,
            "trigger_event": self.trigger_event,
            "status": self.status,
            "conclusion": self.conclusion,
            "stages": json.loads(self.stages_data) if self.stages_data else [],
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class GitHubConfig(Base):
    """Stores GitHub repository connection and access settings."""
    __tablename__ = "github_configs"

    id = Column(Integer, primary_key=True, index=True)
    repo_owner = Column(String(100), nullable=False)
    repo_name = Column(String(100), nullable=False)
    branch = Column(String(80), default="main")
    workflow_filename = Column(String(80), default="tests.yml")
    access_token = Column(String(255), nullable=True)  # Encrypted/masked
    is_connected = Column(Boolean, default=False)
    last_synced_at = Column(DateTime, nullable=True)

    def to_dict(self, mask_token: bool = True) -> Dict[str, Any]:
        token_display = "••••••••••••••••" if self.access_token and mask_token else (self.access_token or "")
        return {
            "id": self.id,
            "repo_owner": self.repo_owner,
            "repo_name": self.repo_name,
            "branch": self.branch,
            "workflow_filename": self.workflow_filename,
            "access_token": token_display,
            "has_token": bool(self.access_token),
            "is_connected": self.is_connected,
            "last_synced_at": self.last_synced_at.isoformat() if self.last_synced_at else None
        }
