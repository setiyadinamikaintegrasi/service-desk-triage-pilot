# Threat Model

**Status:** Pilot assumptions; not a production security assessment.

## Scope

Internal service-desk triage pilot running locally or in a controlled CI test. It is not production-ready and must not be exposed publicly.

## Trust boundaries

| Boundary | Input | Control |
|---|---|---|
| HTTP client → FastAPI | JSON ticket fields | Pydantic validation and bounded lengths |
| FastAPI → repository | Domain objects | Typed models; repository owns persistence |
| Ticket → triage adapter | Title/description/reporter | Deterministic code only; no outbound call |
| Triage result → SQLite | Structured output | `TriageResult` validation before storage |
| CI → repository | Source and test fixtures | gitleaks, dependency/security workflows, review PR |

## Main risks

| Risk | STRIDE/AI | Mitigation | Residual status |
|---|---|---|---|
| Unauthorized API access | Spoofing/Elevation | Authentication is not implemented; keep internal-only | Open follow-up |
| Sensitive ticket text exposure | Information disclosure | No external provider; avoid public deployment/logging | Controlled for pilot |
| Malformed triage result | Tampering/unsafe output | Pydantic schema validation before persistence | Mitigated |
| Prompt injection in future provider adapter | AI prompt injection | Provider adapter and input policy remain future work | Deferred |
| SQLite file exposure | Information disclosure | Local/controlled filesystem only | Controlled for pilot |
| Oversized request | DoS | Pydantic length limits | Mitigated for MVP |
| Secret leakage | Supply-chain | No `AI_EVAL_API_KEY`, no credentials, inherited scans | Mitigated by checks |

## Explicit non-goals

No authentication, authorization, rate limiting, encryption-at-rest, deployment, model provider, or production incident controls are claimed by this pilot. `production_ready=false` remains expected. Do not expose secrets or ticket payloads through logs, public endpoints, or provider calls.
