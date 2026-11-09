# SDET & QA Automation Technical Interview Preparation Guide 🎯
### *Focused on REST API Automation Testing with Python (0–2 Years Experience)*

This guide contains **25+ commonly asked technical interview questions, conceptual breakdowns, and model answers** based directly on the architecture and implementation of this framework.

---

## 📌 Section 1: Framework Architecture & Design

### Q1: Can you walk me through the architecture of your API Automation framework?
**Answer:**
> *"The framework is built using Python, Pytest, and Requests. It follows a modular structure:
> 1. **Target API Layer (`application/`):** A sample microservice built with FastAPI providing realistic CRUD operations, Pydantic data validation, and JWT authentication.
> 2. **Client Utility Layer (`utils/api_client.py`):** An `APIClient` class wrapping `requests.Session`. It centralizes the base URL, sets default JSON headers, attaches Bearer tokens, records response duration in milliseconds, and logs every request and response.
> 3. **Fixtures & Lifecycle (`conftest.py`):** Manages background server health verification, acquires session-scoped auth tokens, and provides setup/teardown fixtures (`created_user`) that clean up test data after execution.
> 4. **Test Suite Layer (`tests/`):** 59 test cases categorized by Pytest markers into functional, negative, authentication, schema, and performance tests.
> 5. **Validation Layer (`schemas/` & `utils/helpers.py`):** Validates contracts against JSON Schema (Draft-7) and asserts response time SLA.
> 6. **Reporting & CI/CD:** Pytest-HTML for execution dashboards, dual-stream file/console logging, and GitHub Actions for continuous integration."*

---

### Q2: Why did you build an `APIClient` wrapper instead of calling `requests.get()` directly in tests?
**Answer:**
> *"Directly using `requests.get()` in every test creates massive code duplication and maintenance overhead. By creating an `APIClient` wrapper:
> - **DRY Principle:** Base URL prefixes, timeouts, and common headers (`Content-Type: application/json`) are defined once.
> - **Session Management:** Using `requests.Session()` reuses TCP connections via HTTP keep-alive, significantly speeding up execution.
> - **Unified Logging:** Every outgoing request (method, URL, headers, body) and incoming response (status, latency, body) is automatically logged without cluttering test methods.
> - **Measurement:** It automatically measures `response.elapsed_ms` for performance SLA assertions.
> - **Auth Token Handling:** `set_bearer_token()` attaches the JWT token to all subsequent calls seamlessly."*

---

### Q3: How do you handle environment-based configuration (e.g., Local vs Staging vs Prod)?
**Answer:**
> *"In `config/config.py`, all critical parameters—such as `BASE_URL`, `TIMEOUT`, and test credentials—are loaded dynamically using `os.getenv()`, with safe fallback defaults:
> ```python
> BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000')
> ```
> This allows switching test environments in CI/CD simply by setting environment variables without modifying a single line of test code."*

---

## 📌 Section 2: Pytest, Fixtures & Test Data Management

### Q4: What is the purpose of `conftest.py` in Pytest?
**Answer:**
> *"In Pytest, `conftest.py` serves as the centralized configuration and shared fixture repository. Any fixture defined in `conftest.py` is automatically discovered by all test files within its directory scope without needing explicit imports. It also houses Pytest lifecycle hooks like `pytest_runtest_makereport` and report customization hooks."*

---

### Q5: How do you ensure test independence and prevent test data pollution?
**Answer:**
> *"I use Pytest fixtures with the `yield` keyword to implement automatic setup and teardown:
> ```python
> @pytest.fixture(scope="function")
> def created_user(authenticated_client):
>     # Setup: Create a temporary user with a unique email
>     user = authenticated_client.post("/users", json=generate_random_user()).json()
>     yield user
>     # Teardown: Always delete the created user
>     authenticated_client.delete(f"/users/{user['id']}")
> ```
> Using UUID-generated unique emails (`qa_user_8f3c7e@example.com`) ensures tests never collide, and the teardown step guarantees the database remains clean even if an assertion in the test fails."*

---

### Q6: What are Pytest fixture scopes and which ones did you use?
**Answer:**
> *- **`function` (default):** Runs once per test function. Used for `created_user` and `authenticated_client` to provide isolation.
> - **`class`:** Runs once per test class.
> - **`module`:** Runs once per test file.
> - **`session`:** Runs once across the entire test run. Used for `ensure_server_running`, `api_client`, and `auth_token`. Acquiring the JWT token once per session avoids making 50 redundant login requests, drastically speeding up the test run.*

---

### Q7: How does Data-Driven Testing work in your framework?
**Answer:**
> *"We implement data-driven testing in two ways:
> 1. **Pytest Parameterization (`@pytest.mark.parametrize`):** Used for testing multiple boundary values (e.g. roles: `admin`, `tester`, `developer`, `guest`, or invalid IDs: `0`, `-1`, `-99`).
> 2. **External JSON Datasets (`test_data/users.json`):** Complex payloads (missing fields, wrong data types, invalid emails) are externalized in JSON files and loaded via fixtures. This separates test logic from test data."*

---

## 📌 Section 3: REST & HTTP Fundamentals

### Q8: What is the difference between `PUT` and `PATCH`?
**Answer:**
> *- **`PUT`:** Full replacement of the target resource. The client must supply the entire payload. In our API, `PUT /users/{id}` replaces all fields (`name`, `email`, `role`, `status`, `age`).
> - **`PATCH`:** Partial update. Only the fields intended to be modified are sent. In our framework, `PATCH /users/{id}` allows updating just `role` or `status` while leaving `name`, `email`, and `age` unchanged.*

---

### Q9: What is the difference between HTTP `400` and `422`?
**Answer:**
> *- **`400 Bad Request`:** The request cannot be understood or is missing essential syntax (e.g., our API returns 400 when an empty JSON `{}` is sent to `PATCH`).
> - **`422 Unprocessable Entity`:** The request syntax is well-formed (valid JSON), but the payload contains semantic validation errors—such as missing mandatory fields, age below 18, or an invalid email format.*

---

### Q10: What is the difference between HTTP `401 Unauthorized` and `403 Forbidden`?
**Answer:**
> *- **`401 Unauthorized`:** Authentication is required and has either failed or not been provided (e.g., missing Bearer token or invalid password).
> - **`403 Forbidden`:** The client is authenticated, but does not have permission to access the requested resource (authorization failure).*

---

### Q11: What is the difference between HTTP `200 OK` and `201 Created`?
**Answer:**
> *- **`200 OK`:** General success for requests that retrieve, update, or delete data without creating a new resource entity.
> - **`201 Created`:** Specific success for resource creation (`POST /users`). It is best practice to also include a `Location` header (e.g., `Location: /users/6`) pointing to the newly created resource.*

---

### Q12: What are idempotent HTTP methods?
**Answer:**
> *"An HTTP method is idempotent if executing it multiple times produces the exact same server state as executing it once.
> - **Idempotent:** `GET`, `PUT`, `DELETE`, `HEAD`, `OPTIONS`.
> - **Non-Idempotent:** `POST` (executing `POST /users` multiple times creates multiple users with different IDs).*

---

## 📌 Section 4: Authentication & Security Testing

### Q13: How does JWT authentication work and how do you test it?
**Answer:**
> *"A JSON Web Token (JWT) consists of three base64url-encoded parts separated by dots: `Header.Payload.Signature`.
> 1. In `test_authentication.py`, we test the **happy path**: calling `POST /login` with valid credentials returns a 200 OK, `token_type: "bearer"`, and an active JWT string.
> 2. We test **negative paths**:
>    - Invalid credentials -> `401 Unauthorized`.
>    - Missing mandatory username/password -> `422 Unprocessable Entity`.
>    - Accessing protected routes without `Authorization` header -> `401 Unauthorized`.
>    - Forged or malformed tokens (`Bearer invalid_token_123`) -> `401 Unauthorized`.
>    - Incorrect auth scheme (`Basic dXNlcjpwYXNz`) -> `401 Unauthorized`."*

---

### Q14: How did you test security vulnerabilities like SQL Injection and XSS in the API?
**Answer:**
> *"In `tests/test_negative_scenarios.py`:
> - **SQL Injection Test:** We inject `' OR 1=1; --` into search query parameters to ensure the API handles the input as literal text without crashing or returning unintended records.
> - **XSS Injection Test:** We send `<script>alert('xss');</script>` in the user `name` field to verify it is stored and retrieved strictly as an escaped/literal string without executing or corrupting the database."*

---

## 📌 Section 5: Contract & Performance Testing

### Q15: Why is JSON Schema validation necessary if we already check `response.status_code == 200`?
**Answer:**
> *"Checking status code 200 only verifies that the server processed the request without throwing a fatal error. It does NOT guarantee that the payload contains all required fields or the correct data types.
> If a developer accidentally renames `user_id` to `id` or changes `age` from integer to string, status 200 will still pass, but client applications (mobile apps, frontends) will crash.
> JSON Schema validation (`jsonschema.validate`) guarantees strict contract adherence by checking field presence, types, regex patterns, and enums."*

---

### Q16: How do you measure and assert API response time SLA in Python?
**Answer:**
> *"In Requests, `response.elapsed.total_seconds() * 1000` gives the round-trip latency in milliseconds.
> Our `APIClient` attaches this value directly as `response.elapsed_ms`.
> In `tests/test_response_validation.py`, we assert:
> ```python
> assert response.elapsed_ms <= 1500.0, f"SLA Violated: took {response.elapsed_ms}ms"
> ```
> We also verified that the FastAPI server includes an `X-Process-Time-Ms` header via custom middleware."*

---

## 📌 Section 6: CI/CD & Reporting

### Q17: How is CI/CD configured in this repository?
**Answer:**
> *"We use GitHub Actions defined in `.github/workflows/tests.yml`.
> - **Trigger:** Runs on every `push` and `pull_request` to `main` or `master`.
> - **Matrix:** Runs across Python `3.11` and `3.12`.
> - **Steps:** Checks out code, sets up Python, installs dependencies from `requirements.txt`, boots the FastAPI server in background, polls `/health` until ready, runs Pytest with HTML reporting, and uploads `reports/report.html` and `execution.log` as build artifacts retained for 14 days."*

---

### Q18: What would you do if a test fails in the CI pipeline?
**Answer:**
> *"1. Check the GitHub Actions Step Summary and download the `report.html` and `execution.log` artifacts.
> 2. Read the failure diagnostic log: inspect the HTTP method, endpoint, status code, and response body preview.
> 3. Identify if the issue is a bug in the code, a contract change, or a flaky test environment (e.g., timeout).
> 4. Reproduce the failure locally by running the specific test: `pytest tests/test_create_users.py -k test_name -s`.
> 5. Log a detailed defect report with Steps to Reproduce, Expected Result, Actual Result, Request Payload, and Server Response."*

