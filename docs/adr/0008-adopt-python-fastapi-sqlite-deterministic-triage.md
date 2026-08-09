# ADR-0008: Adopt single-stack Python and deterministic triage adapter

- **Status:** Accepted for pilot
- **Date:** 2026-08-09

## Context

The consumer project exists to test `template-ai-native` with a realistic single-stack Python API. The MVP needs persistence and an AI-native boundary without requiring a provider credential or external model call.

## Decision

Use Python 3.12, FastAPI, Pydantic, SQLAlchemy 2, and SQLite. Keep the package under `src/service_desk_triage/` with a root `pyproject.toml`.

Define a `TriageAdapter` interface and use `DeterministicTriageAdapter` as the default. Store validated triage output with the ticket. Register prompt metadata and golden cases even though no provider is called.

## Alternatives considered

- Node/Go: rejected for this pilot because the target is single-stack Python template detection and workflow routing.
- Direct provider SDK: rejected because it would require credentials and create provider coupling in business logic.
- In-memory storage: rejected because SQLite persistence is needed to exercise integration behavior.
- PostgreSQL: deferred; unnecessary complexity for the local/internal pilot.

## Consequences

Positive:

- Reproducible local and CI behavior without secrets.
- Clear adapter boundary for future provider integration.
- Small implementation suitable for template adoption audit.

Trade-offs:

- Deterministic rules are limited and not a model-quality claim.
- SQLite is not a production-scale persistence choice.
- Authentication and deployment remain consumer follow-up work.
