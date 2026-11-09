# Enterprise Defect Reports & Bug Tracking Portfolio 📋
### *Sample QA Defect Tickets Discovered During API Automation Testing*

In production environments, discovering defects through automated test runs and documenting them with actionable precision is a critical responsibility of a Software Testing Engineer / SDET.

Below are **real-world defect tickets** modeled after enterprise Jira/Azure DevOps issue formats, based directly on the edge cases and negative scenarios covered by this framework.

---

## 🐞 Defect Ticket #1: DEF-101 - Duplicate Email Registration Handled Inconsistently

| Field | Detail |
|---|---|
| **Issue Key** | `DEF-101` |
| **Project** | User Management Microservice |
| **Component** | User Controller (`/users`) |
| **Issue Type** | Bug |
| **Severity** | High (Major) |
| **Priority** | P2 (High) |
| **Reporter** | QA Automation Engineer |
| **Assignee** | Backend Developer |
| **Status** | Resolved / Verified |
| **Automated Test** | `tests/test_create_users.py::test_create_user_duplicate_email_returns_409` |

### Summary
`POST /users` permits case-insensitive duplicate email creation if spaces or differing letter casing are provided (e.g., `Alice@example.com` vs `alice@example.com`).

### Environment
- **Environment:** Staging / Local CI
- **Application Version:** v1.0.0
- **Base URL:** `http://127.0.0.1:8000`

### Steps to Reproduce
1. Dispatch an authenticated `POST` request to `/users` with payload:
   ```json
   {
     "name": "Alice Johnson",
     "email": "alice@example.com",
     "role": "admin",
     "status": "active",
     "age": 28
   }
   ```
2. Observe successful creation (`201 Created`).
3. Dispatch a second authenticated `POST` request with uppercase email:
   ```json
   {
     "name": "Duplicate Alice",
     "email": "ALICE@EXAMPLE.COM",
     "role": "admin",
     "status": "active",
     "age": 30
   }
   ```

### Expected Result
- Status Code: `409 Conflict`
- Response Body:
  ```json
  {
    "detail": "Email 'alice@example.com' already registered"
  }
  ```

### Actual Result (Before Fix)
- Status Code: `201 Created`
- Duplicate user was registered, violating account uniqueness and causing authentication ambiguity during login.

### Root Cause Analysis (RCA)
The backend database lookup performed strict case-sensitive string matching (`email == user['email']`) rather than normalizing the email using `.strip().lower()`.

### Verification Status
Verified via automated regression test `test_create_user_duplicate_email_returns_409`. Now passes 100%.

---

## 🐞 Defect Ticket #2: DEF-102 - PATCH /users Accepts Empty Payload Without Validation

| Field | Detail |
|---|---|
| **Issue Key** | `DEF-102` |
| **Project** | User Management Microservice |
| **Component** | User Controller (`/users/{user_id}`) |
| **Issue Type** | Bug |
| **Severity** | Medium |
| **Priority** | P3 (Medium) |
| **Reporter** | QA Automation Engineer |
| **Assignee** | Backend Developer |
| **Status** | Resolved / Verified |
| **Automated Test** | `tests/test_update_users.py::test_patch_update_empty_payload_returns_400` |

### Summary
`PATCH /users/{user_id}` returned `200 OK` when an empty JSON object `{}` was sent, resulting in a redundant database write and missing client payload validation.

### Steps to Reproduce
1. Send authenticated request:
   ```bash
   curl -X PATCH http://127.0.0.1:8000/users/1 \
     -H "Authorization: Bearer <VALID_JWT>" \
     -H "Content-Type: application/json" \
     -d '{}'
   ```

### Expected Result
- Status Code: `400 Bad Request`
- Response Body:
  ```json
  {
    "detail": "Empty patch payload: at least one field must be provided for update"
  }
  ```

### Actual Result (Before Fix)
- Status Code: `200 OK`
- Database update executed with zero modifications.

### Fix
Added validation in `application/routes/users.py` checking `if not patch_data: raise HTTPException(status_code=400, ...)`.

---

## 🐞 Defect Ticket #3: DEF-103 - Missing Authorization Scheme Prefix Returned Ambiguous Error

| Field | Detail |
|---|---|
| **Issue Key** | `DEF-103` |
| **Project** | User Management Microservice |
| **Component** | Security & Auth Middleware (`/auth`) |
| **Issue Type** | Bug |
| **Severity** | Medium |
| **Priority** | P3 |
| **Reporter** | QA Automation Engineer |
| **Assignee** | Backend Developer |
| **Status** | Resolved / Verified |
| **Automated Test** | `tests/test_authentication.py::test_access_protected_endpoint_with_malformed_auth_header` |

### Summary
When a non-Bearer scheme header was provided (such as `Authorization: Basic dXNlcjpwYXNz`), the API returned `{"detail": "Missing authentication token"}` instead of alerting the client about the unsupported authentication scheme.

### Expected Result
- Status Code: `401 Unauthorized`
- Response Header: `WWW-Authenticate: Bearer`
- Response Body:
  ```json
  {
    "detail": "Invalid authentication scheme. Expected Bearer token"
  }
  ```

### Actual Result (Before Fix)
- Returned misleading message: `"Missing authentication token"`.

### Fix
Updated `get_current_user` in `application/routes/auth.py` to explicitly validate the header prefix before attempting token extraction.

