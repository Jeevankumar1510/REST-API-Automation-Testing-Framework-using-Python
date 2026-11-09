"""
Intelligent test case generation and Python project scaffolding engine.
Automatically generates positive, negative, authentication, schema, and SLA tests,
and builds production-grade standalone Pytest test suites.
"""

from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional


class GeneratorService:
    """Generates test cases and complete executable Python Pytest projects."""

    @staticmethod
    def slugify(text: str) -> str:
        """Convert path or name into clean Python identifier slug."""
        text = text.replace("/", "_").replace("{", "").replace("}", "").replace("-", "_")
        slug = re.sub(r"[^a-zA-Z0-9_]", "", text)
        return slug.strip("_").lower() or "root"

    @classmethod
    def generate_test_cases(
        cls,
        endpoints: List[Dict[str, Any]],
        auth_type: str = "none",
        auth_token: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Intelligently generates positive, negative, authentication, and SLA test cases
        for a collection of endpoints.
        """
        generated_tests: List[Dict[str, Any]] = []

        for ep in endpoints:
            path = ep.get("path", "/")
            method = ep.get("method", "GET").upper()
            slug = cls.slugify(path)
            expected_status = ep.get("expected_status", 200)
            auth_required = ep.get("auth_required", False) or auth_type != "none"
            request_body = ep.get("request_body")

            # Replace {param} in path with sample values for positive testing
            positive_path = re.sub(r"\{[^}]+\}", "1", path)

            # Headers
            default_headers = {"Content-Type": "application/json", "Accept": "application/json"}
            if auth_required and auth_token:
                default_headers["Authorization"] = f"Bearer {auth_token}"

            # -------------------------------------------------------------
            # 1. POSITIVE / FUNCTIONAL TEST CASES
            # -------------------------------------------------------------
            positive_test = {
                "name": f"test_{method.lower()}_{slug}_success_{expected_status}",
                "category": "functional",
                "description": f"Verify {method} {path} returns HTTP {expected_status} with valid input.",
                "http_method": method,
                "url_path": positive_path,
                "headers": default_headers,
                "params": {},
                "payload": request_body if method in ["POST", "PUT", "PATCH"] else None,
                "expected_status": expected_status,
                "is_enabled": True,
                "is_approved": True
            }
            generated_tests.append(positive_test)

            # -------------------------------------------------------------
            # 2. SLA PERFORMANCE TEST CASE
            # -------------------------------------------------------------
            sla_test = {
                "name": f"test_{method.lower()}_{slug}_response_time_sla",
                "category": "performance",
                "description": f"Verify response time of {method} {path} complies with SLA (< 1500ms).",
                "http_method": method,
                "url_path": positive_path,
                "headers": default_headers,
                "params": {},
                "payload": request_body if method in ["POST", "PUT", "PATCH"] else None,
                "expected_status": expected_status,
                "is_enabled": True,
                "is_approved": True
            }
            generated_tests.append(sla_test)

            # -------------------------------------------------------------
            # 3. NEGATIVE TEST CASES (Missing Fields / Wrong Types / 404 / 422)
            # -------------------------------------------------------------
            # If path has path variables (e.g., /users/{id})
            if "{" in path:
                # 404 Non-existent ID
                nonexistent_path = re.sub(r"\{[^}]+\}", "99999", path)
                generated_tests.append({
                    "name": f"test_{method.lower()}_{slug}_nonexistent_resource_returns_404",
                    "category": "negative",
                    "description": f"Verify {method} {path} returns 404 for non-existent ID 99999.",
                    "http_method": method,
                    "url_path": nonexistent_path,
                    "headers": default_headers,
                    "params": {},
                    "payload": request_body if method in ["POST", "PUT", "PATCH"] else None,
                    "expected_status": 404,
                    "is_enabled": True,
                    "is_approved": True
                })

                # 422 Invalid Type for Path Parameter
                invalid_type_path = re.sub(r"\{[^}]+\}", "invalid-string-id", path)
                generated_tests.append({
                    "name": f"test_{method.lower()}_{slug}_invalid_id_type_returns_422",
                    "category": "negative",
                    "description": f"Verify {method} {path} returns 422 when path ID is not an integer.",
                    "http_method": method,
                    "url_path": invalid_type_path,
                    "headers": default_headers,
                    "params": {},
                    "payload": None,
                    "expected_status": 422,
                    "is_enabled": True,
                    "is_approved": True
                })

            # If request body exists (POST/PUT/PATCH)
            if request_body and isinstance(request_body, dict):
                # Negative: Missing mandatory field
                keys = list(request_body.keys())
                if keys:
                    first_key = keys[0]
                    corrupt_body = deepcopy(request_body)
                    del corrupt_body[first_key]
                    generated_tests.append({
                        "name": f"test_{method.lower()}_{slug}_missing_{first_key}_returns_422",
                        "category": "negative",
                        "description": f"Verify {method} {path} rejects payload missing mandatory field '{first_key}'.",
                        "http_method": method,
                        "url_path": positive_path,
                        "headers": default_headers,
                        "params": {},
                        "payload": corrupt_body,
                        "expected_status": 422,
                        "is_enabled": True,
                        "is_approved": True
                    })

                # Negative: Incorrect data type (string instead of int/bool)
                corrupt_type_body = deepcopy(request_body)
                for k, v in corrupt_type_body.items():
                    if isinstance(v, (int, float, bool)):
                        corrupt_type_body[k] = "invalid_string_datatype"
                        generated_tests.append({
                            "name": f"test_{method.lower()}_{slug}_invalid_type_{k}_returns_422",
                            "category": "negative",
                            "description": f"Verify {method} {path} returns 422 when '{k}' is assigned invalid type.",
                            "http_method": method,
                            "url_path": positive_path,
                            "headers": default_headers,
                            "params": {},
                            "payload": corrupt_type_body,
                            "expected_status": 422,
                            "is_enabled": True,
                            "is_approved": True
                        })
                        break

            # -------------------------------------------------------------
            # 4. AUTHENTICATION TEST CASES
            # -------------------------------------------------------------
            if auth_required:
                # Missing Token (401)
                no_auth_headers = {k: v for k, v in default_headers.items() if k.lower() != "authorization"}
                generated_tests.append({
                    "name": f"test_{method.lower()}_{slug}_missing_token_returns_401",
                    "category": "auth",
                    "description": f"Verify unauthenticated request to {method} {path} returns HTTP 401 Unauthorized.",
                    "http_method": method,
                    "url_path": positive_path,
                    "headers": no_auth_headers,
                    "params": {},
                    "payload": request_body if method in ["POST", "PUT", "PATCH"] else None,
                    "expected_status": 401,
                    "is_enabled": True,
                    "is_approved": True
                })

                # Invalid / Forged Token (401)
                bad_auth_headers = deepcopy(default_headers)
                bad_auth_headers["Authorization"] = "Bearer invalid.forged.jwt.token.12345"
                generated_tests.append({
                    "name": f"test_{method.lower()}_{slug}_invalid_token_returns_401",
                    "category": "auth",
                    "description": f"Verify {method} {path} rejects invalid Bearer token with HTTP 401.",
                    "http_method": method,
                    "url_path": positive_path,
                    "headers": bad_auth_headers,
                    "params": {},
                    "payload": request_body if method in ["POST", "PUT", "PATCH"] else None,
                    "expected_status": 401,
                    "is_enabled": True,
                    "is_approved": True
                })

        return generated_tests

    @classmethod
    def generate_project_scaffold(
        cls,
        project_name: str,
        base_url: str,
        test_cases: List[Dict[str, Any]],
        output_dir: Path
    ) -> Dict[str, str]:
        """
        Builds a complete, modular, runnable Python Pytest automation project on disk.
        Returns a mapping of relative file paths to their generated source code.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "tests").mkdir(parents=True, exist_ok=True)
        (output_dir / "utils").mkdir(parents=True, exist_ok=True)
        (output_dir / "config").mkdir(parents=True, exist_ok=True)
        (output_dir / "reports").mkdir(parents=True, exist_ok=True)
        (output_dir / ".github" / "workflows").mkdir(parents=True, exist_ok=True)

        generated_files: Dict[str, str] = {}

        # 1. requirements.txt
        req_content = (
            "requests>=2.31.0\n"
            "pytest>=8.0.0\n"
            "pytest-html>=4.1.0\n"
            "pytest-metadata>=3.1.0\n"
            "jsonschema>=4.20.0\n"
        )
        generated_files["requirements.txt"] = req_content

        # 2. pytest.ini
        ini_content = (
            "[pytest]\n"
            "testpaths = tests\n"
            "python_files = test_*.py\n"
            "python_classes = Test*\n"
            "python_functions = test_*\n"
            "addopts = -v -s --html=reports/report.html --self-contained-html\n"
            "markers =\n"
            "    smoke: Critical path smoke tests\n"
            "    functional: Core CRUD and functional logic tests\n"
            "    negative: Negative tests, boundary conditions, and invalid inputs\n"
            "    auth: Authentication and token validation tests\n"
            "    performance: API response time SLA tests\n"
        )
        generated_files["pytest.ini"] = ini_content

        # 3. config/config.py
        cfg_content = f'''"""
Centralized Configuration for {project_name}.
"""
import os

BASE_URL = os.getenv("API_BASE_URL", "{base_url.rstrip('/')}")
DEFAULT_TIMEOUT = float(os.getenv("API_TIMEOUT", "10.0"))
MAX_RESPONSE_TIME_MS = float(os.getenv("MAX_RESPONSE_TIME_MS", "1500.0"))
'''
        generated_files["config/config.py"] = cfg_content
        generated_files["config/__init__.py"] = ""

        # 4. utils/api_client.py
        client_content = '''"""
Reusable HTTP API Client wrapper around requests.Session.
"""
import time
import requests

class APIClient:
    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = path if path.startswith("http") else f"{self.base_url}/{path.lstrip('/')}"
        kwargs.setdefault("timeout", self.timeout)
        start = time.perf_counter()
        resp = self.session.request(method.upper(), url, **kwargs)
        resp.elapsed_ms = (time.perf_counter() - start) * 1000
        return resp

    def get(self, path: str, **kwargs): return self.request("GET", path, **kwargs)
    def post(self, path: str, **kwargs): return self.request("POST", path, **kwargs)
    def put(self, path: str, **kwargs): return self.request("PUT", path, **kwargs)
    def patch(self, path: str, **kwargs): return self.request("PATCH", path, **kwargs)
    def delete(self, path: str, **kwargs): return self.request("DELETE", path, **kwargs)
'''
        generated_files["utils/api_client.py"] = client_content
        generated_files["utils/__init__.py"] = ""

        # 5. conftest.py
        conftest_content = '''"""
Pytest configuration and global fixtures.
"""
import pytest
from config.config import BASE_URL, DEFAULT_TIMEOUT
from utils.api_client import APIClient

@pytest.fixture(scope="session")
def client() -> APIClient:
    return APIClient(base_url=BASE_URL, timeout=DEFAULT_TIMEOUT)
'''
        generated_files["conftest.py"] = conftest_content

        # 6. Group test cases by category
        categories = {"functional": [], "negative": [], "auth": [], "performance": []}
        for tc in test_cases:
            cat = tc.get("category", "functional")
            if cat not in categories:
                cat = "functional"
            categories[cat].append(tc)

        # Generate test files for each category
        for cat_name, cases in categories.items():
            if not cases:
                continue

            lines = [
                f'"""',
                f'Automated Test Suite for {cat_name.capitalize()} Scenarios.',
                f'Generated by Intelligent API Automation Platform.',
                f'"""',
                f'import pytest',
                f'from utils.api_client import APIClient',
                f'from config.config import MAX_RESPONSE_TIME_MS',
                f'',
                f'@pytest.mark.{cat_name}',
                f'class Test{cat_name.capitalize()}Scenarios:',
                f''
            ]

            for tc in cases:
                fn_name = tc.get("name", f"test_{cat_name}")
                desc = tc.get("description", "")
                method = tc.get("http_method", "GET").lower()
                path = tc.get("url_path", "/")
                headers = tc.get("headers", {})
                params = tc.get("params", {})
                payload = tc.get("payload")
                exp_status = tc.get("expected_status", 200)

                lines.extend([
                    f'    def {fn_name}(self, client: APIClient):',
                    f'        """{desc}"""',
                    f'        headers = {json.dumps(headers)}',
                    f'        params = {json.dumps(params)}',
                    f'        payload = {json.dumps(payload)}',
                    f'        response = client.{method}("{path}", headers=headers, params=params, json=payload)',
                    f'        assert response.status_code == {exp_status}, (',
                    f'            f"Expected status {exp_status}, but received {{response.status_code}}. "',
                    f'            f"Response body: {{response.text[:300]}}"',
                    f'        )'
                ])

                if cat_name == "performance":
                    lines.extend([
                        f'        assert response.elapsed_ms <= MAX_RESPONSE_TIME_MS, (',
                        f'            f"SLA Violated: latency {{response.elapsed_ms:.2f}}ms > {{MAX_RESPONSE_TIME_MS}}ms"',
                        f'        )'
                    ])

                lines.append('')

            filename = f"tests/test_{cat_name}.py"
            generated_files[filename] = "\n".join(lines)

        # 7. CI/CD Workflow
        workflow_content = f'''name: Automated Test Pipeline - {project_name}

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  run-api-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"
      - name: Install Dependencies
        run: pip install -r requirements.txt
      - name: Execute Automated Tests
        run: pytest -v --html=reports/report.html --self-contained-html
      - name: Upload Test Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: api-test-report
          path: reports/report.html
'''
        generated_files[".github/workflows/tests.yml"] = workflow_content

        # 8. README.md
        readme_content = f'''# {project_name} - API Automation Testing Suite

Automated REST API testing suite generated by the **Intelligent API Automation & CI/CD Platform**.

- **Target Base URL:** `{base_url}`
- **Framework:** Python, Pytest, Requests
- **Test Scenarios:** {len(test_cases)} automated test cases

## How to Execute Tests

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run all tests with HTML report
pytest

# 3. Run selective test markers
pytest -m functional
pytest -m negative
pytest -m auth
pytest -m performance
```
'''
        generated_files["README.md"] = readme_content

        # Write all files to disk
        for rel_path, content in generated_files.items():
            file_path = output_dir / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

        return generated_files

