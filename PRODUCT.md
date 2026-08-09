# PRODUCT.md

**Status:** Approved pilot scope — internal only, not production-ready.

## Product vision

Service Desk Triage Pilot membantu tim internal mencatat ticket service desk dan mendapatkan triage awal yang konsisten melalui adapter deterministik yang dapat diganti dengan adapter AI provider-neutral pada fase berikutnya.

## Problem

Ticket internal sering datang dengan informasi tidak seragam. Pilot ini menguji apakah API sederhana dapat menyimpan ticket, memfilter backlog, dan menghasilkan category, priority, summary, confidence, serta reasoning code yang dapat diaudit.

## Users

- Service desk operator.
- Internal employees sebagai reporter.
- Engineering/platform team sebagai evaluator template.

## MVP scope

- Health endpoint.
- Create, list, filter, dan retrieve ticket.
- Deterministic triage.
- Status `open`, `in_progress`, `resolved`.
- Priority `critical`, `high`, `medium`, `low`.
- SQLite persistence.
- OpenAPI, tests, golden evaluation cases, dan package build.

## Explicit non-goals

- Pilot/internal only; belum production-ready.
- Authentication dan authorization belum termasuk MVP.
- Tidak ada deployment atau production infrastructure.
- Tidak memanggil model provider nyata.
- Tidak menyimpan secret atau credential.
- `production_ready=false` tetap expected dari template readiness contract.

## Success measures

- Onboarding dari template dan initializer dapat diverifikasi.
- API MVP berjalan melalui test dan smoke verification.
- Coverage keseluruhan minimal 80%.
- Deterministic golden cases pass tanpa API key.
- Quality, security, documentation, dan build gates dapat dijalankan.
- Tidak ada direct provider SDK di business logic.
