"""
Automated Test Suite for Upgraded Platform Services & Modules (Modules 1 - 8).
Validates 3D pipeline endpoints, project wizard, specification parsing, test generation,
execution engine, ZIP packaging, and dashboard analytics.
"""

import json
from typing import Any, Dict
import pytest
from utils.api_client import APIClient
from utils.helpers import assert_status_code


@pytest.mark.functional
@pytest.mark.regression
class TestPlatformUpgrade:
    """Test suite covering the Intelligent API Automation & CI/CD Platform capabilities."""

    def test_platform_ui_endpoint_returns_html(self, api_client: APIClient):
        """Verify GET /platform serves the web platform interface."""
        response = api_client.get("/platform")
        assert_status_code(response, 200)
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "Antigravity | Intelligent API Automation" in response.text

    def test_dashboard_stats_endpoint(self, api_client: APIClient):
        """Verify GET /api/platform/dashboard/stats returns high-level platform KPIs."""
        response = api_client.get("/api/platform/dashboard/stats")
        assert_status_code(response, 200)

        body = response.json()
        assert "total_projects" in body and body["total_projects"] >= 1
        assert "total_endpoints" in body and body["total_endpoints"] >= 1
        assert "total_test_cases" in body and body["total_test_cases"] >= 1
        assert "success_percentage" in body
        assert "avg_latency_ms" in body
        assert "latest_pipeline_status" in body

    def test_dashboard_charts_endpoint(self, api_client: APIClient):
        """Verify GET /api/platform/dashboard/charts returns chart datasets."""
        response = api_client.get("/api/platform/dashboard/charts")
        assert_status_code(response, 200)

        body = response.json()
        assert "trend" in body
        assert "labels" in body["trend"]
        assert "passed" in body["trend"]
        assert "categories" in body
        assert len(body["categories"]["data"]) == 5

    def test_list_projects(self, api_client: APIClient):
        """Verify GET /api/platform/projects returns list of projects."""
        response = api_client.get("/api/platform/projects")
        assert_status_code(response, 200)

        projects = response.json()
        assert isinstance(projects, list)
        assert len(projects) >= 1
        assert any(p["name"] == "User Management REST API" for p in projects)

    def test_create_and_delete_project(self, api_client: APIClient):
        """Verify project lifecycle: create, retrieve, and delete."""
        payload = {
            "name": "Integration Test E-Commerce Service",
            "description": "Automated e-commerce checkout testing suite",
            "app_type": "ecommerce",
            "base_url": "https://api.example.com",
            "language": "Python",
            "framework": "Pytest + Requests"
        }
        create_res = api_client.post("/api/platform/projects", json=payload)
        assert_status_code(create_res, 201)
        project_id = create_res.json()["id"]

        # Retrieve
        get_res = api_client.get(f"/api/platform/projects/{project_id}")
        assert_status_code(get_res, 200)
        assert get_res.json()["name"] == payload["name"]

        # Delete
        del_res = api_client.delete(f"/api/platform/projects/{project_id}")
        assert_status_code(del_res, 200)

    def test_parse_openapi_specification(self, api_client: APIClient):
        """Verify parsing raw OpenAPI JSON specification and generating suggested tests."""
        sample_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Sample Bookstore API", "version": "1.0"},
            "servers": [{"url": "https://api.bookstore.com"}],
            "paths": {
                "/books": {
                    "get": {
                        "summary": "List Books",
                        "responses": {"200": {"description": "OK"}}
                    },
                    "post": {
                        "summary": "Create Book",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "title": {"type": "string", "example": "The Pragmatic Programmer"},
                                            "price": {"type": "number", "example": 39.99}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {"201": {"description": "Created"}}
                    }
                }
            }
        }

        form_data = {
            "spec_type": "openapi",
            "raw_content": json.dumps(sample_spec)
        }
        response = api_client.post("/api/platform/projects/parse-spec", data=form_data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert_status_code(response, 200)

        body = response.json()
        assert body["meta"]["title"] == "Sample Bookstore API"
        assert len(body["endpoints"]) == 2
        assert len(body["suggested_tests"]) >= 4

    def test_parse_postman_collection(self, api_client: APIClient):
        """Verify parsing Postman collection JSON."""
        sample_collection = {
            "info": {"name": "Orders Postman API", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
            "variable": [{"key": "base_url", "value": "https://orders.example.com"}],
            "item": [
                {
                    "name": "Get Orders",
                    "request": {"method": "GET", "url": "{{base_url}}/orders"}
                }
            ]
        }

        form_data = {
            "spec_type": "postman",
            "raw_content": json.dumps(sample_collection)
        }
        response = api_client.post("/api/platform/projects/parse-spec", data=form_data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert_status_code(response, 200)

        body = response.json()
        assert body["meta"]["title"] == "Orders Postman API"
        assert len(body["endpoints"]) == 1

    def test_scaffold_code_preview(self, api_client: APIClient):
        """Verify previewing generated Python project files (conftest, pytest.ini, tests, etc.)."""
        # Using Project ID 1 (User Management)
        response = api_client.get("/api/platform/projects/1/scaffold-preview")
        assert_status_code(response, 200)

        body = response.json()
        assert "files" in body
        files = body["files"]
        assert "requirements.txt" in files
        assert "pytest.ini" in files
        assert "conftest.py" in files
        assert "utils/api_client.py" in files
        assert "tests/test_functional.py" in files
        assert ".github/workflows/tests.yml" in files

    def test_project_zip_download(self, api_client: APIClient):
        """Verify downloading full project as a valid ZIP file."""
        response = api_client.get("/api/platform/projects/1/download-zip")
        assert_status_code(response, 200)
        assert response.headers.get("Content-Type") == "application/zip"
        assert len(response.content) > 500

    def test_pipeline_latest_returns_11_stages(self, api_client: APIClient):
        """Verify 3D CI/CD pipeline returns all 11 required DevOps stages."""
        response = api_client.get("/api/platform/pipeline/latest")
        assert_status_code(response, 200)

        body = response.json()
        assert "stages" in body
        stages = body["stages"]
        assert len(stages) == 11

        expected_stage_names = [
            "Developer Code", "Git Repository", "GitHub Webhook",
            "CI/CD Trigger", "Dependency Installation", "Code Quality Checks",
            "Pytest Execution", "API Test Execution", "Test Result Validation",
            "HTML Report Generation", "Deployment / Release Status"
        ]
        for idx, expected_name in enumerate(expected_stage_names, start=1):
            matching = [s for s in stages if s["id"] == idx or expected_name in s["name"]]
            assert len(matching) > 0, f"Stage #{idx} '{expected_name}' missing from pipeline"

    def test_pipeline_simulation_run(self, api_client: APIClient):
        """Verify triggering interactive 3D pipeline simulation."""
        payload = {"branch": "feature/test-automation", "trigger_event": "manual"}
        response = api_client.post("/api/platform/pipeline/simulate", json=payload)
        assert_status_code(response, 200)

        body = response.json()
        assert body["status"] == "completed"
        assert body["conclusion"] == "success"
        assert len(body["stages"]) == 11

    def test_execute_test_suite_endpoint(self, api_client: APIClient):
        """Verify triggering live execution against target API and receiving execution record."""
        # Execute smoke or functional tests on Project ID 1
        payload = {
            "project_id": 1,
            "execution_type": "functional"
        }
        response = api_client.post("/api/platform/execution/run", json=payload)
        assert_status_code(response, 200)

        body = response.json()
        assert body["project_id"] == 1
        assert body["total_tests"] >= 1
        assert body["status"] in ["passed", "completed", "failed"]
        assert "output_logs" in body and len(body["output_logs"]) > 20
        assert "report_path" in body
