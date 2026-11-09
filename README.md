# REST API Automation Testing Framework & Intelligent 3D CI/CD Platform 🚀

[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Testing Framework](https://img.shields.io/badge/Testing-Pytest%20v8.3-orange?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![API Backend](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![HTTP Client](https://img.shields.io/badge/HTTP-Requests-blueviolet)](https://requests.readthedocs.io/)
[![3D Visualization](https://img.shields.io/badge/3D%20Engine-Three.js-black?logo=three.js&logoColor=white)](https://threejs.org/)
[![ORM & Database](https://img.shields.io/badge/Database-SQLite%20%2B%20SQLAlchemy-red?logo=sqlite&logoColor=white)](https://www.sqlalchemy.org/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An **industry-standard, enterprise-grade REST API Test Automation and CI/CD Management Platform** written in Python and modern Web technologies. Built as a flagship portfolio and production engineering showcase, this system demonstrates practical automation engineering, software testing architecture, and DevOps orchestration for **Software Testing Engineers, SDETs, and Full-Stack Automation Architects**.

The platform combines a **78-test Pytest + Requests automation test suite** against a production-like **FastAPI microservice** with an interactive **Three.js 3D CI/CD DevOps Pipeline Visualizer**, a **7-Step Project Generator Wizard** (supporting OpenAPI JSON/YAML, Postman Collections, and URL auto-probing), **persistent SQLite/SQLAlchemy project management**, **live execution telemetry with streaming terminal logs**, and **bidirectional GitHub Actions integration**.

---

## 📑 Table of Contents
1. [Platform Highlights & Core Modules](#-platform-highlights--core-modules)
2. [Interactive Web Platform Showcase (How to Run)](#-interactive-web-platform-showcase-how-to-run)
3. [Enterprise System Architecture](#-enterprise-system-architecture)
4. [Module 1: Interactive 3D CI/CD Pipeline Visualizer](#-module-1-interactive-3d-cicd-pipeline-visualizer)
5. [Module 2: + CREATE NEW AUTOMATION PROJECT Wizard](#-module-2--create-new-automation-project-wizard)
6. [Module 3: Projects Management Dashboard](#-module-3-projects-management-dashboard)
7. [Module 4: Advanced Test Execution Dashboard & Analytics](#-module-4-advanced-test-execution-dashboard--analytics)
8. [Module 5: GitHub Actions CI/CD Integration](#-module-5-github-actions-cicd-integration)
9. [Module 6: Security, Performance SLAs & Reliability](#-module-6-security-performance-slas--reliability)
10. [Folder Structure](#-folder-structure)
11. [Target REST API Microservice Specification](#-target-rest-api-microservice-specification)
12. [Automated Test Suites & Pytest Markers (78 Tests)](#-automated-test-suites--pytest-markers-78-tests)
13. [Reporting & Centralized Dual-Stream Logging](#-reporting--centralized-dual-stream-logging)
14. [SDET Interview Talking Points](#-sdet-interview-talking-points)
15. [License](#-license)

---

## 🌟 Platform Highlights & Core Modules

| Module | Capability | Implementation Details |
|---|---|---|
| **Module 1: 3D DevOps Pipeline** | 11 Connected CI/CD Stages | Interactive Three.js 3D scene, glowing status rings, animated data flow particles, stage detail inspector modal. |
| **Module 2: Project Creation Wizard** | 7-Step Intelligent Generator | Supports OpenAPI 3.0/2.0 (JSON/YAML), Postman Collections v2.0/v2.1, and Live URL auto-probing (`/docs`, `/openapi.json`). |
| **Module 3: Scaffolding & ZIP Export** | Automated Code Generator | Generates standalone Pytest automation frameworks (`conftest.py`, `pytest.ini`, `api_client.py`, tests, workflows) with one-click `.zip` export. |
| **Module 4: Execution Engine** | Live API Test Runner | Real-time test dispatch, SLA latency benchmarking, and auto-compiled self-contained HTML reports (`reports/executions/`). |
| **Module 5: My Projects Hub** | SQLite & SQLAlchemy ORM | Persistent project cards, execution history, seed projects (*User Management* & *E-Commerce Store*), and instant execution. |
| **Module 6: Analytics Dashboard** | Real-Time Metrics & Charts | Pass/Fail trends, category breakdown (Functional, Negative, Auth, Schema, SLA), response time tracking, and streaming terminal output. |
| **Module 7: CI/CD Sync** | GitHub Actions REST API | Connects to GitHub API to monitor live pipeline runs, inspect stage-by-stage job status, and trigger workflow dispatches. |
| **Module 8: Security & Reliability** | Safe Parsing & Sanitization | Masked tokens, timeout guards, sanitized file exports, and boundary validation across all endpoints. |

---

## 🖥 Interactive Web Platform Showcase (How to Run)

The platform offers multiple effortless ways to run and demonstrate the application:

```
  ┌────────────────────────────────────────────────────────────────────────┐
  │ 🌟 Web Platform:        http://127.0.0.1:8000/platform                 │
  │ 📖 Swagger Docs:        http://127.0.0.1:8000/docs                     │
  │ 📊 3D Canvas Standalone: Open dashboard.html in your browser           │
  └────────────────────────────────────────────────────────────────────────┘
```

### Option A: The All-in-One Interactive CLI Menu (Recommended)
Double-click `run.bat` or run:
```powershell
python run_tests.py
```
This launches the interactive command center:
```text
=================================================================
  🧪 REST API AUTOMATION TESTING FRAMEWORK - TEST RUNNER
=================================================================
  [1] Run All Automated Tests (Full Regression Suite)
  [2] Run Smoke Tests (Critical Path Verification)
  [3] Run Authentication & Token Tests
  [4] Run Negative Scenarios (400, 401, 404, 405, 409, 422)
  [5] Run JSON Schema & Performance SLA Tests
  [6] Open Latest HTML Test Report in Browser
  [7] Open Web Platform (3D CI/CD & Project Wizard) [Browser]
  [8] Open Interactive 3D Architecture Canvas
  [9] Run Concurrency & Load Benchmark (100 reqs / 10 workers)
  [10] Start FastAPI Target Application & Platform Server
  [0] Exit
=================================================================
```

### Option B: Start Server & Open Web Platform in Browser
```powershell
# 1. Start application and platform server
python -m uvicorn application.main:app --host 127.0.0.1 --port 8000 --reload --reload-dir application

# 2. Open in your browser:
# http://127.0.0.1:8000/platform
```

### Option C: Run Complete 78-Test Automated Regression Suite
```powershell
python -m pytest
```
*Note: Pytest automatically boots the target server in the background via the session fixture in `conftest.py` if not already running!*

---

## 🏗 Enterprise System Architecture

```
                          ┌────────────────────────────────────────┐
                          │   Frontend Web Platform & 3D Engine    │
                          │      (application/static/index.html)   │
                          ├────────────────────────────────────────┤
                          │  • Three.js 3D 11-Stage Pipeline       │
                          │  • 7-Step + Create Project Wizard      │
                          │  • Projects Grid & Real-time Runner    │
                          │  • Chart.js Trend & Analytics Graphs   │
                          │  • Live Streaming Terminal Output      │
                          └───────────────────┬────────────────────┘
                                              │ HTTP / JSON API
                                              ▼
 ┌──────────────────────────────────────────────────────────────────────────────────────────────┐
 │                              FastAPI Application Server (Port 8000)                          │
 ├──────────────────────────────────────────────┬───────────────────────────────────────────────┤
 │     Target Microservices Under Test          │       Intelligent Platform Core Routers       │
 ├──────────────────────────────────────────────┼───────────────────────────────────────────────┤
 │ • /login, /auth/verify (JWT Bearer Auth)     │ • /api/platform/projects (CRUD, Spec Parser)  │
 │ • /users, /users/{id} (CRUD, Search, Filter) │ • /api/platform/execution (Runner Engine)     │
 │ • /health, /reset-db                         │ • /api/platform/pipeline (3D Pipeline Status) │
 │ • In-Memory Seed User Database               │ • /api/platform/github (GitHub Actions Sync)  │
 │                                              │ • /api/platform/dashboard (KPI Metrics)       │
 └──────────────────────┬───────────────────────┴───────────────────────┬───────────────────────┘
                        │                                               │
                        ▼                                               ▼
         ┌─────────────────────────────┐                 ┌─────────────────────────────┐
         │     SQLite & SQLAlchemy     │                 │   Automation Services       │
         │  (platform_core/platform.db)│                 │  • ParserService (OpenAPI)  │
         │  • Projects, Endpoints      │                 │  • GeneratorService (Pytest)│
         │  • TestCases, Executions    │                 │  • RunnerService (Live Run) │
         │  • PipelineRuns, GitHubCfg  │                 │  • GitHubService (Live API) │
         └─────────────────────────────┘                 └──────────────┬──────────────┘
                                                                        │
                                                ┌───────────────────────┴───────────────────────┐
                                                ▼                                               ▼
                                 ┌─────────────────────────────┐                 ┌─────────────────────────────┐
                                 │   Generated Project ZIP     │                 │   Stand-Alone HTML Reports  │
                                 │   (Complete Pytest Suite)   │                 │   & Execution Logs (.log)   │
                                 └─────────────────────────────┘                 └─────────────────────────────┘
```

---

## 🎮 Module 1: Interactive 3D CI/CD Pipeline Visualizer

An interactive 3D DevOps pipeline powered by **Three.js** that models continuous integration and continuous deployment:

### 1. The 11 Connected DevOps Stages:
1. **Developer Code**: Local developer changes and commit staging.
2. **Git Repository**: Branch synchronization, PR validation, and Git tree tracking.
3. **GitHub Webhook**: Event routing and payload dispatch to CI runners.
4. **CI/CD Trigger**: Workflow initiation, matrix build initialization (Python 3.11 & 3.12).
5. **Dependency Installation**: Pip caching, wheels compilation, and virtual environment provisioning.
6. **Code Quality Checks**: Flake8 linting, Black formatting, and type assertions.
7. **Pytest Execution**: Automated discovery and execution of the Pytest suite.
8. **API Test Execution**: Real HTTP calls against live endpoints via `APIClient`.
9. **Test Result Validation**: Status code assertions, contract JSON schemas, and SLA latency verification.
10. **HTML Report Generation**: Interactive HTML report compilation with diagnostic metadata.
11. **Deployment / Release Status**: Production gating and release delivery.

### 2. 3D Visual Features:
- **Glowing Neon Platforms**: Color-coded by state: Green (Passed), Red (Failed), Yellow (In Progress), Blue/Purple (Queued).
- **Moving Data Flow Particles**: 45+ animated Three.js particles continuously stream between interconnected processing nodes.
- **Interactive OrbitControls**: Smooth 360° mouse rotation, zoom in/out, and panning.
- **Stage Detail Inspector Modal**: Clicking any 3D node opens a comprehensive telemetry card with execution duration, passed/failed test counts, commit hashes, and raw execution logs.
- **Live Pipeline Simulation**: Click **"⚡ Simulate Pipeline Run"** to watch the visualizer sequentially animate each stage in real time.

---

## 🧙‍♂️ Module 2: + CREATE NEW AUTOMATION PROJECT Wizard

The platform features an intelligent, guided 7-step wizard that turns any API specification or URL into an executable, production-grade Pytest automation framework:

```
[ Step 1: Info ] ➔ [ Step 2: Spec / URL ] ➔ [ Step 3: Endpoints ] ➔ [ Step 4: Scenarios ]
                 ➔ [ Step 5: Code Preview ] ➔ [ Step 6: Live Execution ] ➔ [ Step 7: Export ZIP ]
```

- **Step 1: Project Details**: Configure project name, target type (REST API, Microservice, E-Commerce, Auth Service), description, and default test timeout.
- **Step 2: API Specification Input**:
  - **Auto-Discovery URL Probe**: Enter a base URL (e.g. `http://127.0.0.1:8000`), and the system automatically checks `/openapi.json`, `/docs`, and `/swagger.json`.
  - **OpenAPI 3.0 / 2.0 (JSON & YAML)**: Paste raw specification or Swagger schemas.
  - **Postman Collections (v2.0 & v2.1)**: Import exported Postman collection JSON.
  - **Manual Endpoint Builder**: Add endpoints on the fly with HTTP methods, paths, and sample JSON payloads.
- **Step 3: Endpoint Review**: Inspect parsed endpoints, path variables, query parameters, and required HTTP headers.
- **Step 4: Automated Test Generation**: Automatically generates test matrices:
  - Happy Path / Positive Functional Tests (200 OK, 201 Created).
  - Negative & Boundary Tests (404 Not Found, 422 Invalid Type, Missing Fields).
  - Authentication Tests (Missing Bearer Token, Invalid Token).
  - Performance SLA Tests (< 1500ms latency threshold).
- **Step 5: Code Scaffold Preview**: Inspect generated Python code files before saving:
  - `requirements.txt`
  - `pytest.ini`
  - `conftest.py` (with fixtures and server lifecycle)
  - `utils/api_client.py` (with session pooling and logging)
  - `tests/test_functional.py` & `tests/test_negative.py`
  - `.github/workflows/tests.yml`
- **Step 6: Live Test Execution**: Execute the generated tests against the live endpoint with real-time feedback.
- **Step 7: Instant ZIP Download**: Download a complete, self-contained project `.zip` archive ready to open in VS Code, PyCharm, or run in any CI/CD environment.

---

## 📁 Module 3: Projects Management Dashboard

- **Persistent SQLite Storage**: Backed by `platform_core/platform.db` using SQLAlchemy ORM with automatic schema migrations.
- **Pre-Seeded Industry Showcases**:
  1. *User Management REST API*: Full CRUD and JWT authentication suite.
  2. *E-Commerce Store API*: Product catalog, cart management, and checkout validation.
- **Project Cards**: Display endpoint counts, test scenario counts, base URLs, and last execution status.
- **One-Click Actions**:
  - **Run Tests**: Execute the suite against the target API immediately.
  - **View Report**: Open standalone HTML execution report.
  - **Download ZIP**: Export generated Python framework.
  - **Delete Project**: Safely remove project and cascade records.

---

## 📈 Module 4: Advanced Test Execution Dashboard & Analytics

- **Top-Level KPI Metrics**:
  - Total Active Automation Projects
  - Total Cataloged Endpoints
  - Total Automated Test Cases
  - Aggregate Success Rate (%)
  - Average API Latency (ms)
- **Interactive Chart.js Visualizations**:
  - **Test Execution Trend**: 7-day rolling pass vs fail historical bar chart.
  - **Test Category Breakdown**: Polar/Doughnut chart mapping Functional, Negative, Authentication, Schema, and Performance distributions.
- **Live Streaming Terminal**: Embedded console capturing real-time test execution logs with ANSI styling, timestamped request/response logging, and pass/fail indicators.

---

## 🐙 Module 5: GitHub Actions CI/CD Integration

- **Repository Connection**: Connect any GitHub repository (`owner/repo`) with optional Personal Access Token (PAT).
- **Security & Privacy**: Access tokens are securely transmitted and masked; never exposed in frontend code.
- **Live Workflow Telemetry**:
  - Real-time workflow status (queued, in_progress, completed).
  - Run conclusion (success, failure, cancelled).
  - Commit ID, branch name, trigger event, duration, and job steps.
- **One-Click Workflow Dispatch**: Trigger manual GitHub Actions runs directly from the web interface.

---

## 🛡 Module 6: Security, Performance SLAs & Reliability

- **Token Masking**: All authentication headers and sensitive API tokens are sanitized and masked in logs (`Bearer eyJhbGci...****`).
- **File & Path Traversal Protection**: Exported ZIP files and file writes sanitize all paths, strictly preventing directory traversal attacks.
- **Timeout Protection**: All test calls enforce HTTP timeouts (default 10s) to prevent thread exhaustion or hanging test runs.
- **Thread-Safe Test Data Lifecycle**: Pytest fixtures use UUID-generated records with automatic setup and teardown, guaranteeing zero database pollution between test runs.

---

## 📂 Folder Structure

```
Python_API_Automation/
│
├── application/                         # Target FastAPI Application & Web Platform
│   ├── main.py                         # Lifespan context, router mounts, root content negotiation
│   ├── models.py                       # Pydantic data schemas for requests and responses
│   ├── database.py                     # Thread-safe in-memory database with initial seed users
│   ├── routes/                         # Modular API route controllers
│   │   ├── auth.py                     # Authentication, JWT generation, /login route
│   │   └── users.py                    # User CRUD routes (GET, POST, PUT, PATCH, DELETE)
│   └── static/
│       └── index.html                  # Intelligent Web Platform & Three.js 3D CI/CD Visualizer
│
├── platform_core/                       # Intelligent Automation Platform Core Architecture
│   ├── database.py                     # SQLite engine & SQLAlchemy session maker
│   ├── models.py                       # ORM Models (Project, Endpoint, TestCase, Execution, Pipeline)
│   ├── schemas.py                      # Pydantic validation schemas for platform APIs
│   ├── routes/                         # Platform API controllers
│   │   ├── projects_routes.py          # /api/platform/projects (CRUD, Spec parser, ZIP download)
│   │   ├── execution_routes.py         # /api/platform/execution (Runner engine & HTML reports)
│   │   ├── pipeline_routes.py          # /api/platform/pipeline (11-stage CI/CD visualizer API)
│   │   ├── github_routes.py            # /api/platform/github (GitHub Actions REST sync)
│   │   └── dashboard_routes.py         # /api/platform/dashboard (KPI stats and Chart.js feeds)
│   └── services/                       # Platform Business Logic Services
│       ├── parser_service.py           # OpenAPI 2.0/3.0, Postman, and URL auto-discovery parser
│       ├── generator_service.py        # Automated Pytest suite and project scaffolding generator
│       ├── runner_service.py           # Test execution engine and HTML report compiler
│       ├── project_service.py          # Project lifecycle and ZIP packager
│       └── github_service.py           # GitHub Actions REST API service
│
├── tests/                              # Automated Pytest Test Suites (78 Test Cases)
│   ├── test_get_users.py               # Verification of GET /users collection & GET /users/{id}
│   ├── test_create_users.py            # POST /users success, duplicate email (409), boundaries
│   ├── test_update_users.py            # PUT (full replace) and PATCH (partial update) tests
│   ├── test_delete_users.py            # DELETE /users/{id} and post-delete verification
│   ├── test_authentication.py          # /login positive & negative, missing/invalid JWT tokens
│   ├── test_negative_scenarios.py      # 404, 405, bad types, negative IDs, XSS & SQLi safety
│   ├── test_response_validation.py     # JSON schema contract, Python data types, SLA response time
│   └── test_platform_upgrade.py        # 12 Automated tests verifying Platform Modules 1 - 8
│
├── utils/                              # Reusable Framework Utilities
│   ├── api_client.py                   # Reusable HTTP client wrapping requests.Session with logging
│   ├── logger.py                       # Centralized dual console/file logging setup
│   └── helpers.py                      # Schema validator, random generators, test data loaders
│
├── schemas/                            # JSON Schema Contracts
│   └── user_schema.json                # Draft-7 JSON Schema for User entity & User List
│
├── test_data/                          # Externalized Test Data
│   └── users.json                      # Valid and invalid payloads for data-driven testing
│
├── reports/                            # Test Deliverables & Execution Artifacts
│   ├── execution.log                   # Detailed HTTP traffic and event log
│   ├── report.html                     # Self-contained Pytest-HTML execution report
│   └── executions/                     # Platform execution reports generated dynamically
│
├── config/                             # Centralized Configuration
│   └── config.py                       # Environment configuration using os.getenv
│
├── .github/
│   └── workflows/
│       └── tests.yml                   # GitHub Actions CI/CD workflow pipeline
│
├── conftest.py                         # Pytest fixtures, server lifecycle hook, HTML hooks
├── pytest.ini                          # Pytest CLI options, custom markers, and log formats
├── requirements.txt                    # Pinned production and test dependencies
├── run_tests.py                        # Interactive CLI test runner & management utility
├── run.bat                             # One-click Windows runner batch script
├── load_test.py                        # Concurrency and benchmark load testing script
├── dashboard.html                      # Standalone interactive 3D architecture dashboard
└── README.md                           # Comprehensive documentation
```

---

## 📡 Target REST API Microservice Specification

When the FastAPI server is running (`http://127.0.0.1:8000`), interactive Swagger UI documentation is accessible at `http://127.0.0.1:8000/docs`.

| Method | Endpoint | Auth Required | Description | Success Code | Error Codes |
|---|---|:---:|---|:---:|:---:|
| `GET` | `/health` | No | Service health check | `200 OK` | `500` |
| `POST` | `/login` | No | Authenticate user & issue JWT token | `200 OK` | `401`, `422` |
| `GET` | `/auth/verify` | **Yes** | Verify active Bearer token validity | `200 OK` | `401` |
| `GET` | `/users` | No | Retrieve paginated users list with filters | `200 OK` | `422` |
| `GET` | `/users/{id}` | No | Retrieve specific user by ID | `200 OK` | `404`, `422` |
| `POST` | `/users` | **Yes** | Create a new user with unique email | `201 Created` | `401`, `409`, `422` |
| `PUT` | `/users/{id}` | **Yes** | Fully update an existing user record | `200 OK` | `401`, `404`, `409`, `422` |
| `PATCH` | `/users/{id}` | **Yes** | Partially update specific user fields | `200 OK` | `400`, `401`, `404`, `409`, `422` |
| `DELETE`| `/users/{id}` | **Yes** | Delete user permanently | `200 OK` | `401`, `404`, `422` |
| `POST` | `/reset-db` | No | Reset database to initial seed data | `200 OK` | `500` |

### Default Test Credentials:
| Username | Password | Role |
|---|---|---|
| `testuser@example.com` | `SecretPass123!` | Tester |
| `admin@example.com` | `AdminPass123!` | Administrator |
| `qa_engineer` | `Testing123!` | QA Engineer |

---

## 🧪 Automated Test Suites & Pytest Markers (78 Tests)

The framework includes **78 fully automated test cases** (66 core microservice tests + 12 platform upgrade tests):

### Pytest Markers:
| Marker | Command | Purpose |
|---|---|---|
| **Smoke** | `pytest -m smoke` | Fast path health check on core endpoints |
| **Regression** | `pytest -m regression` | Full regression coverage across all 78 tests |
| **Functional** | `pytest -m functional` | Core CRUD functional validation |
| **Negative** | `pytest -m negative` | Error handling, boundaries, missing fields, bad types |
| **Authentication** | `pytest -m auth` | Token generation, missing token, invalid scheme |
| **Contract / Schema** | `pytest -m schema` | JSON Schema compliance checks |
| **Performance** | `pytest -m performance` | Response time SLA verification (< 1500ms) |

### Example Commands:
```powershell
# Run smoke tests
python -m pytest -m smoke

# Run authentication test suite
python -m pytest -m auth

# Run negative scenarios
python -m pytest -m negative

# Run platform upgrade tests
python -m pytest tests/test_platform_upgrade.py

# Run all tests with verbose output
python -m pytest -v
```

---

## 📊 Reporting & Centralized Dual-Stream Logging

### 1. Pytest-HTML Execution Dashboard
Every test execution generates an HTML report at `reports/report.html`.
- Overall Pass / Fail / Skipped breakdown.
- Execution duration per test.
- Detailed failure diagnostics (request method, URL, expected vs actual status code, response body preview) without needing screenshots.
- Open with: `Start-Process reports/report.html` on Windows.

### 2. Centralized Execution Logs (`reports/execution.log`)
Every outgoing HTTP request and incoming HTTP response is automatically captured:
```log
2026-11-09 16:45:07 | INFO     | [APIClient] ===> REQUEST: POST http://127.0.0.1:8000/login
2026-11-09 16:45:07 | INFO     | [APIClient] <=== RESPONSE: 200 OK in 15.22ms [http://127.0.0.1:8000/login]
2026-11-09 16:45:08 | INFO     | [APIClient] ===> REQUEST: POST http://127.0.0.1:8000/users
2026-11-09 16:45:08 | INFO     | [APIClient] <=== RESPONSE: 201 Created in 12.44ms [http://127.0.0.1:8000/users]
```

---

## 💡 SDET Interview Talking Points

*Tips for presenting this platform during a technical interview:*

1. **"How did you design the API Client?"**
   > *"I designed an `APIClient` class wrapping `requests.Session`. Instead of writing raw requests in every test, it centralizes the base URL, sets default JSON headers, manages Bearer authentication tokens, tracks latency in milliseconds, and logs every request and response to both stdout and a persistent file log."*

2. **"How do you handle test data and cleanup?"**
   > *"I used Pytest fixtures with Python's `yield` statement in `conftest.py`. For tests requiring an existing user, the `created_user` fixture executes a POST request during setup with a unique UUID email, yields that user to the test, and immediately sends a DELETE request during teardown. This ensures complete test isolation without polluting the database."*

3. **"Why did you implement JSON Schema validation?"**
   > *"Status code 200 alone does not prove an API is functioning correctly. If a field type changes or a required key is dropped, the API might still return 200, but client applications will crash. By validating responses against Draft-7 JSON Schemas using `jsonschema`, we enforce contract compliance, required field presence, data types, and value formats."*

4. **"How does your platform generate automated tests from specifications?"**
   > *"We implemented a modular `ParserService` supporting OpenAPI 3.0/2.0 JSON/YAML, Postman Collections, and URL auto-probing. It extracts paths, parameters, and bodies, then passes them to `GeneratorService`, which creates targeted positive tests, negative boundary checks, auth validation, and performance SLA assertions, packaging them into a downloadable standalone Python project."*

5. **"What inspired the 3D CI/CD visualization?"**
   > *"DevOps pipelines are often black boxes for teams. Using Three.js, we created an interactive 3D visualization that represents each stage of the DevOps pipeline—from code commit to linting, Pytest execution, contract verification, and HTML reporting. It provides glowing visual status cues, particle data flow, and clickable stage telemetry."*

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
