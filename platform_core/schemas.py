"""
Pydantic schemas for the Intelligent API Automation Platform requests and responses.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# Project Schemas
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    description: Optional[str] = ""
    app_type: str = Field(default="custom", description="ecommerce, banking, healthcare, user_management, custom")
    base_url: str = Field(..., min_length=4)
    language: str = "Python"
    framework: str = "Pytest + Requests"
    auth_type: str = Field(default="none", description="none, bearer, basic, api_key")
    auth_token: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    app_type: Optional[str] = None
    base_url: Optional[str] = None
    auth_type: Optional[str] = None
    auth_token: Optional[str] = None
    status: Optional[str] = None


# Endpoint Schemas
class EndpointCreate(BaseModel):
    path: str = Field(..., min_length=1)
    method: str = Field(..., description="GET, POST, PUT, PATCH, DELETE")
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[List[Dict[str, Any]]] = None
    request_body: Optional[Dict[str, Any]] = None
    expected_status: int = 200
    auth_required: bool = False


# Test Case Schemas
class TestCaseCreate(BaseModel):
    name: str
    category: str = "functional"  # functional, positive, negative, auth, schema, performance
    description: Optional[str] = None
    http_method: str
    url_path: str
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    payload: Optional[Dict[str, Any]] = None
    expected_status: int = 200
    expected_schema: Optional[Dict[str, Any]] = None
    is_enabled: bool = True
    is_approved: bool = True


class TestCaseUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    http_method: Optional[str] = None
    url_path: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    payload: Optional[Dict[str, Any]] = None
    expected_status: Optional[int] = None
    is_enabled: Optional[bool] = None
    is_approved: Optional[bool] = None


# Execution Schemas
class ExecutionRequest(BaseModel):
    project_id: int
    execution_type: str = "all"  # all, functional, negative, auth, selected
    test_case_ids: Optional[List[int]] = None


# Spec Import Schemas
class OpenAPISpecImport(BaseModel):
    project_name: Optional[str] = None
    app_type: Optional[str] = "custom"
    base_url: Optional[str] = None
    spec_text: str  # JSON or YAML string


class PostmanCollectionImport(BaseModel):
    project_name: Optional[str] = None
    app_type: Optional[str] = "custom"
    base_url: Optional[str] = None
    collection_json: Dict[str, Any]


# GitHub Config Schemas
class GitHubConfigCreate(BaseModel):
    repo_owner: str
    repo_name: str
    branch: str = "main"
    workflow_filename: str = "tests.yml"
    access_token: Optional[str] = None


class PipelineTriggerRequest(BaseModel):
    project_id: Optional[int] = None
    branch: str = "main"
    trigger_event: str = "manual"

