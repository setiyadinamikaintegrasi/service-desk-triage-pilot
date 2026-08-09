# Service Desk Triage MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the internal-only Service Desk Triage Pilot MVP with Python 3.12, FastAPI, SQLite persistence, deterministic triage, prompt registry metadata, and meaningful tests.

**Architecture:** Use a small source package under `src/service_desk_triage/` with API, database, models, repository, and triage adapter boundaries. Store tickets in SQLite through SQLAlchemy and validate all request/response shapes with Pydantic. Keep AI behavior provider-neutral by using a `TriageAdapter` interface plus deterministic default.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2, SQLite, pytest, pytest-cov, ruff, mypy.

## Global Constraints

- Work only in this repository.
- Do not modify inherited `.github/workflows` before the first hosted PR run.
- Do not create symlinks, duplicate manifests, fake tests, secrets, weak default accounts, provider SDK calls, `pull_request_target`, or production deployment.
- Do not commit or push.
- TDD is mandatory; tests must fail before implementation and real failure output must be saved at `/tmp/service-desk-triage-tdd-failure.log`.
- MVP is pilot/internal only, not production-ready, no auth in MVP, no deployment, no real model provider, `production_ready=false`.

---

### Task 1: Failing Tests and Tooling Manifest

**Files:**
- Create: `pyproject.toml`
- Create: `tests/conftest.py`
- Create: `tests/unit/test_ticket_models.py`
- Create: `tests/unit/test_triage_adapter.py`
- Create: `tests/unit/test_evaluation_cases.py`
- Create: `tests/integration/test_ticket_repository.py`
- Create: `tests/e2e/test_api.py`

**Interfaces:**
- Consumes: None.
- Produces: Tests that define the service package contract and fail until implementation exists.

- [ ] **Step 1: Add root Python project metadata**

  Create `pyproject.toml` with Python 3.12 requirement, runtime dependencies, pytest paths, ruff config, mypy strict settings, and package discovery under `src`.

- [ ] **Step 2: Write failing model and adapter tests**

  Cover request validation, status transition rules, structured triage output validation, and five deterministic golden evaluation cases.

- [ ] **Step 3: Write failing persistence and API tests**

  Cover SQLite persistence, create/get/list/filter endpoints, invalid input, consistent not-found, and triage endpoint behavior.

- [ ] **Step 4: Capture red run**

  Run targeted tests and save output with:

  ```sh
  python3 -m pytest -q tests/unit tests/integration tests/e2e > /tmp/service-desk-triage-tdd-failure.log 2>&1
  ```

### Task 2: Minimal Application Implementation

**Files:**
- Create: `src/service_desk_triage/__init__.py`
- Create: `src/service_desk_triage/api.py`
- Create: `src/service_desk_triage/config.py`
- Create: `src/service_desk_triage/database.py`
- Create: `src/service_desk_triage/main.py`
- Create: `src/service_desk_triage/models.py`
- Create: `src/service_desk_triage/repository.py`
- Create: `src/service_desk_triage/triage.py`

**Interfaces:**
- Consumes: Test contracts from Task 1.
- Produces: `create_app()`, SQLAlchemy-backed ticket repository, and deterministic triage adapter.

- [ ] **Step 1: Implement schemas and domain validation**

  Define status and priority enums, ticket create/read/list schemas, triage schemas, and status transition validation.

- [ ] **Step 2: Implement SQLite persistence**

  Define a `TicketRecord` table, session factory, schema initialization, ticket creation, lookup, filtered listing, and triage update.

- [ ] **Step 3: Implement deterministic triage**

  Categorize and prioritize tickets from keyword rules and return validated `TriageResult` values with confidence and reasoning codes.

- [ ] **Step 4: Implement FastAPI routes**

  Add `/health`, `/api/v1/tickets`, `/api/v1/tickets/{id}`, and `/api/v1/tickets/{id}/triage` with consistent JSON 404 errors.

### Task 3: Prompt, Evaluation, and Documentation

**Files:**
- Modify: `prompts/registry.yaml`
- Create: `prompts/tasks/service-desk-triage.md`
- Create: `prompts/schemas/service-desk-triage-input.json`
- Create: `prompts/schemas/service-desk-triage-output.json`
- Create: `evals/golden/service-desk-triage-golden.jsonl`
- Modify: `evals/config/eval-default.yaml`
- Modify: `evals/run-evals.sh`
- Modify: `PRODUCT.md`
- Modify: `DESIGN.md`
- Modify: `ARCHITECTURE.md`
- Create: `docs/adr/0008-adopt-python-fastapi-sqlite-deterministic-triage.md`
- Modify: `docs/adr/README.md`
- Modify: `docs/api/openapi.yaml`
- Modify: `docs/security/threat-model.md`
- Modify: `CHANGELOG.md`
- Create: `docs/verification/template-adoption-report.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: Implemented runtime contract.
- Produces: Provider-neutral prompt/eval metadata and updated consumer project documentation.

- [ ] **Step 1: Register prompt and golden cases**

  Add service-desk prompt metadata, input/output JSON schemas, five golden cases, and eval runner fixture validation for the new dataset.

- [ ] **Step 2: Update docs proportionally**

  Replace template baseline language where needed with internal pilot scope, no auth in MVP, no deployment, no real provider, and `production_ready=false`.

- [ ] **Step 3: Verify and self-review**

  Run format, lint, typecheck, unit/integration/e2e tests, coverage, build, eval check, docs/readiness/project checks, then inspect `git diff`.
