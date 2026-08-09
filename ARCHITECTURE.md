# ARCHITECTURE.md

**Status:** Approved MVP architecture — internal pilot, not production-ready.

## Topology

```text
Client
  │ HTTP/JSON
  ▼
FastAPI routes ── Pydantic schemas
  │
  ├── TicketRepository ── SQLAlchemy ── SQLite
  └── TriageAdapter interface
          └── DeterministicTriageAdapter
```

## Boundaries

- `main.py`: application factory and HTTP routing.
- `models.py`: Pydantic/domain enums, validation, serialization.
- `repository.py`: persistence operations; no provider calls.
- `database.py`: SQLAlchemy engine, ORM record, schema initialization.
- `triage.py`: provider-neutral adapter contract and deterministic implementation.
- `prompts/`: registry, prompt metadata, schemas, and evaluation fixtures.

## AI-native boundary

Business logic depends on `TriageAdapter`, not on an LLM SDK. The deterministic adapter is the only default implementation. A future provider adapter must validate output through `TriageResult` before persistence and must not be imported by domain logic.

## Deployment status

No deployment is configured. No production target, authentication, secret manager, observability backend, or external model provider is included. The template readiness contract must remain `production_ready=false`.

## Risks and limitations

- SQLite is suitable for the pilot only.
- Authentication and authorization are intentionally absent.
- Keyword rules are deterministic and not equivalent to model intelligence.
- Status transition endpoint is not exposed in this MVP; the domain guard exists for future workflow work.
