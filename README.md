# REST API Automation Testing Framework using Python 🚀

[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Testing Framework](https://img.shields.io/badge/Testing-Pytest%20v8.3-orange?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![API Backend](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![HTTP Client](https://img.shields.io/badge/HTTP-Requests-blueviolet)](https://requests.readthedocs.io/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An **industry-standard, production-grade REST API Test Automation Framework** written in Python. This repository is built as a portfolio project demonstrating practical, hands-on automation expertise required for a **Software Testing Engineer / SDET role (0–2 years experience)**.

The framework pairs a fully-functional **FastAPI backend** (providing realistic CRUD endpoints, JWT Bearer authentication, and validation) with a robust **Pytest + Requests automation test suite** featuring custom reporting, schema validation, data-driven tests, and CI/CD integration.

---

## 📑 Table of Contents
1. [Project Overview](#-project-overview)
2. [Framework Architecture](#-framework-architecture)
3. [Technology Stack & Justification](#-technology-stack--justification)
4. [Folder Structure](#-folder-structure)
5. [Target REST API Specification](#-target-rest-api-specification)
6. [Installation & Setup](#-installation--setup)
7. [Running the Application & Tests](#-running-the-application--tests)
8. [Test Design & Coverage](#-test-design--coverage)
9. [Reporting & Centralized Logging](#-reporting--centralized-logging)
10. [CI/CD Pipeline (GitHub Actions)](#-cicd-pipeline-github-actions)
11. [SDET Interview Talking Points](#-sdet-interview-talking-points)

---

## 🎯 Project Overview

This project simulates real-world enterprise test automation where QA engineers test microservices through automated functional, contract, and security validation before release.

### Core Capabilities:
- **Comprehensive Functional Testing:** End-to-end CRUD verification for User entities (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`).
- **Deep Negative Testing:** Handling 400 Bad Request, 401 Unauthorized, 404 Not Found, 405 Method Not Allowed, 409 Conflict, and 422 Unprocessable Entity.
- **Contract & Schema Validation:** Validating response payload contracts against standard Draft-7 JSON Schemas using `jsonschema`.
- **JWT Authentication Testing:** Token generation, expired/invalid tokens, missing auth headers, and scheme validation.
- **Data-Driven Parameterization:** Externalizing test datasets in `users.json` and leveraging `@pytest.mark.parametrize`.
- **Performance SLA Assertions:** Validating API response time limits (< 1500ms) with automated time tracking.
- **Non-Intrusive Test Isolation:** Automatic fixture teardown ensuring zero data pollution between tests.
- **Self-Contained Reporting:** Professional HTML execution reports and centralized dual-stream logging (Console + File).

---

## 🏗 Framework Architecture

```
                  ┌────────────────────────────────────────────────────────┐
                  │                 GitHub Actions CI/CD                   │
                  │   (Triggers on push/PR, boots API, executes tests)     │
                  └───────────────────────────┬────────────────────────────┘
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
         ┌─────────────────────────┐                     ┌─────────────────────────┐
         │   FastAPI Application   │                     │  Pytest Test Automation │
         │   (Target Microservice) │                     │        Framework        │
         ├─────────────────────────┤                     ├─────────────────────────┤
         │ • /login (JWT Token)    │ ◄─── HTTP (JSON) ───┤ • Tests (CRUD, Auth)    │
         │ • /users (CRUD)         │      Port 8000      │ • APIClient (Requests)  │
         │ • /health (Monitoring)  │                     │ • Fixtures (conftest)   │
         │ • In-Memory Data Store  │                     │ • JSON Schema Validator │
         └─────────────────────────┘                     └────────────┬────────────┘
                                                                      │
                                                ┌─────────────────────┴─────────────────────┐
                                                ▼                                           ▼
                                   ┌───────────────────────────┐               ┌───────────────────────────┐
                                   │   HTML Test Report        │               │  Centralized File Log     │
                                   │  (reports/report.html)    │               │  (reports/execution.log)  │
                                   └───────────────────────────┘               └───────────────────────────┘
```

---

## 🧰 Technology Stack & Justification

| Technology | Role | Why it was chosen |
|---|---|---|
| **Python 3.11+** | Programming Language | Highly readable, industry standard for QA automation, rich ecosystem. |
| **Pytest** | Test Automation Runner | Powerful fixture dependency injection, parameterization, flexible CLI markers. |
| **Requests** | HTTP Client | De-facto Python HTTP library with intuitive session management and connection pooling. |
| **FastAPI + Uvicorn** | Backend Under Test | Blazing fast, asynchronous ASGI framework with automated OpenAPI 3.0 docs. |
| **Pydantic v2** | Data Modeling | Strict request/response payload validation and schema modeling. |
| **JSON Schema** | Contract Testing | Enforces strict API contracts, catches unintended schema regressions and breaking changes. |
| **Pytest-HTML** | Test Reporting | Generates standalone, interactive HTML execution dashboards with pass/fail charts. |
| **Python Logging** | Audit & Debugging | Centralized file and console logging capturing every HTTP request and response. |
| **GitHub Actions** | Continuous Integration | Automated regression validation on every pull request and push to main. |

---

## 📂 Folder Structure

```
Python_API_Automation/
│
├── application/                     # Target FastAPI Application
│   ├── __init__.py
│   ├── main.py                     # FastAPI entry point, middleware, routes mounting
│   ├── models.py                   # Pydantic data schemas for requests and responses
│   ├── database.py                 # Thread-safe in-memory database with initial seed users
│   └── routes/                     # Modular API route controllers
│       ├── __init__.py
│       ├── auth.py                 # Authentication, JWT generation, /login route
│       └── users.py                # User CRUD routes (GET, POST, PUT, PATCH, DELETE)
│
├── tests/                          # Automated Pytest Test Suites (59 automated tests)
│   ├── __init__.py
│   ├── test_get_users.py           # Verification of GET /users collection & GET /users/{id}
│   ├── test_create_users.py        # POST /users success, duplicate email (409), boundaries
│   ├── test_update_users.py        # PUT (full replace) and PATCH (partial update) tests
│   ├── test_delete_users.py        # DELETE /users/{id} and post-delete verification
│   ├── test_authentication.py      # /login positive & negative, missing/invalid JWT tokens
│   ├── test_negative_scenarios.py  # 404, 405, bad types, negative IDs, XSS & SQLi safety
│   └── test_response_validation.py # JSON schema contract, Python data types, SLA response time
│
├── utils/                          # Reusable Framework Utilities
│   ├── __init__.py
│   ├── api_client.py               # Reusable HTTP client wrapping requests.Session with logging
│   ├── logger.py                   # Centralized dual console/file logging setup
│   └── helpers.py                  # Schema validator, random generators, test data loaders
│
├── schemas/                        # JSON Schema Contracts
│   └── user_schema.json            # Draft-7 JSON Schema for User entity & User List
│
├── test_data/                      # Externalized Test Data
│   └── users.json                  # Valid and invalid payloads for data-driven testing
│
├── reports/                        # Test Deliverables & Execution Artifacts
│   ├── .gitkeep
│   ├── execution.log               # Detailed HTTP traffic and event log
│   └── report.html                 # Self-contained Pytest-HTML execution report
│
├── config/                         # Environment & Test Configuration
│   ├── __init__.py
│   └── config.py                   # Centralized configuration class using os.getenv
│
├── .github/
│   └── workflows/
│       └── tests.yml               # GitHub Actions CI/CD workflow pipeline
│
├── conftest.py                     # Global Pytest fixtures, server lifecycle hook, HTML hooks
├── pytest.ini                      # Pytest CLI options, custom markers, and log formats
├── requirements.txt                # Pinned production and test dependencies
├── .gitignore                      # Git exclusion rules
└── README.md                       # Comprehensive framework documentation
```

---

## 📡 Target REST API Specification

Interactive Swagger UI documentation is available at `http://127.0.0.1:8000/docs` when the server is running.

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

### Default Test Credentials

| Username | Password | Role |
|---|---|---|
| `testuser@example.com` | `SecretPass123!` | Tester |
| `admin@example.com` | `AdminPass123!` | Administrator |
| `qa_engineer` | `Testing123!` | QA Engineer |

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.11 or Python 3.12 installed on your system.
- Git installed.

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/REST-API-Automation-Testing-Framework-using-Python.git
cd "REST API Automation Testing Framework using Python"
```

### 2. Create and Activate Virtual Environment
**On Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🚀 Running the Application & Tests

### Method A: Automated In-Session Execution (Recommended)
You do **not** need to manually start the server before running tests! The framework's `conftest.py` contains a smart session fixture `ensure_server_running` that automatically starts Uvicorn in the background if the server isn't already active.

Simply run:
```bash
python -m pytest
```

### Method B: Manual Server Startup (Interactive Exploration)
If you want to manually test or explore the Swagger UI documentation:

1. **Start FastAPI Application:**
   ```bash
   python -m uvicorn application.main:app --host 127.0.0.1 --port 8000 --reload
   ```
2. Open your browser and navigate to:
   - **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
   - **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

3. In another terminal window, run the tests:
   ```bash
   python -m pytest
   ```

---

## 🧪 Test Design & Coverage

The test suite contains **59 automated test cases** covering every facet of modern API testing:

### 1. Selective Test Execution with Pytest Markers

The framework defines custom markers in `pytest.ini` for targeted test runs:

| Marker | Command | Purpose |
|---|---|---|
| **Smoke** | `pytest -m smoke` | Fast path health check on core endpoints (8 tests) |
| **Regression** | `pytest -m regression` | Full regression coverage across all endpoints (59 tests) |
| **Functional** | `pytest -m functional` | Core CRUD functional validation |
| **Negative** | `pytest -m negative` | Error handling, boundaries, missing fields, bad types |
| **Authentication** | `pytest -m auth` | Token generation, missing token, invalid scheme |
| **Contract / Schema** | `pytest -m schema` | JSON Schema compliance checks |
| **Performance** | `pytest -m performance` | Response time SLA verification |

### 2. Examples of Running Specific Tests

- **Run only smoke tests:**
  ```bash
  python -m pytest -m smoke
  ```

- **Run only authentication tests:**
  ```bash
  python -m pytest -m auth
  ```

- **Run only negative scenario tests:**
  ```bash
  python -m pytest -m negative
  ```

- **Run a specific test file:**
  ```bash
  python -m pytest tests/test_create_users.py
  ```

- **Run tests and print console stdout/logs:**
  ```bash
  python -m pytest -s -v
  ```

---

## 📊 Reporting & Centralized Logging

### 1. Pytest-HTML Execution Dashboard
Every test execution automatically generates a self-contained HTML report located at:
```
reports/report.html
```

**Features of the Report:**
- Overall Pass / Fail / Skipped metrics with execution duration.
- Test case names, module breakdown, and execution timestamps.
- Detailed failure diagnostics (request method, URL, expected vs actual status code, response body preview) without needing screenshots.
- Environment metadata (OS, Python version, Base URL, Execution time).

To view the report on Windows:
```powershell
Start-Process reports/report.html
```
Or open `reports/report.html` in any web browser.

### 2. Centralized Execution Logs (`reports/execution.log`)
Every outgoing HTTP request and incoming HTTP response is automatically captured with timestamp, log level, HTTP method, URL, latency (ms), and payload:

```log
2026-11-09 15:38:46 | INFO     | [APIClient] ===> REQUEST: POST http://127.0.0.1:8000/login
2026-11-09 15:38:46 | INFO     | [APIClient] <=== RESPONSE: 200 OK in 19.94ms [http://127.0.0.1:8000/login]
2026-11-09 15:38:47 | INFO     | [APIClient] ===> REQUEST: POST http://127.0.0.1:8000/users
2026-11-09 15:38:47 | INFO     | [APIClient] <=== RESPONSE: 201 Created in 19.44ms [http://127.0.0.1:8000/users]
2026-11-09 15:38:47 | INFO     | [APIClient] ===> REQUEST: DELETE http://127.0.0.1:8000/users/6
2026-11-09 15:38:47 | INFO     | [APIClient] <=== RESPONSE: 200 OK in 3.06ms [http://127.0.0.1:8000/users/6]
```

---

## 🔄 CI/CD Pipeline (GitHub Actions)

The repository includes a ready-to-use GitHub Actions workflow configured in [`.github/workflows/tests.yml`](.github/workflows/tests.yml).

### Pipeline Workflow:
1. **Trigger:** Runs automatically on every `push` and `pull_request` to `main`/`master` branch, or manually via `workflow_dispatch`.
2. **Matrix Build:** Tests against Python `3.11` and `3.12` on `ubuntu-latest`.
3. **Dependency Caching:** Uses pip caching for fast build execution.
4. **Target Server Launch:** Boots FastAPI in the background and validates readiness via a Python polling healthcheck.
5. **Test Execution:** Executes full Pytest test suite with `--html=reports/report.html`.
6. **Artifact Archival:** Uploads `report.html` and `execution.log` as downloadable GitHub Actions artifacts retained for 14 days.
7. **Job Summary:** Publishes a Markdown summary card directly on GitHub Step Summary.

---

## 💡 SDET Interview Talking Points

*Tips for explaining this framework during a technical interview for a Software Testing Engineer role (0–2 years experience):*

### 1. "How did you design the API Client?"
> *"I designed an `APIClient` class wrapping `requests.Session`. Instead of writing raw `requests.get` in every test, the client centralizes the base URL, sets default JSON headers, handles Bearer authentication tokens, automatically measures response time in milliseconds, and logs every single request and response to both stdout and `reports/execution.log`."*

### 2. "How do you handle test data and cleanup?"
> *"I used Pytest fixtures with Python's `yield` statement in `conftest.py`. For tests requiring an existing user, the `created_user` fixture executes a POST request during setup to generate a dedicated user with a unique UUID email, yields that user to the test, and immediately sends a DELETE request during teardown. This ensures complete test isolation without polluting the database."*

### 3. "Why did you implement JSON Schema validation?"
> *"Status code 200 alone does not prove an API is working correctly. If a backend developer changes a field from integer to string or renames a key, status code 200 might still be returned, but the frontend will crash. By validating responses against Draft-7 JSON Schemas using `jsonschema.validate`, we enforce contract compliance, required field presence, data types, and value formats."*

### 4. "How does the framework handle positive vs negative testing?"
> *"We separate tests logically: positive tests verify happy paths (200 OK, 201 Created with Location headers), while negative tests verify edge conditions such as non-existent IDs (404), duplicate emails (409 Conflict), missing mandatory fields (422), and unauthorized access (401). We also test boundary values like age limits and inject XSS/SQL characters to verify input sanitization."*

### 5. "How is CI/CD integrated?"
> *"We configured a GitHub Actions pipeline that triggers on push and pull requests. It sets up Python, installs dependencies, launches the FastAPI server in background, verifies health on `http://127.0.0.1:8000/health`, runs Pytest, and archives the generated HTML report and execution logs as build artifacts."*

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
