# DESIGN.md

**Status:** Approved MVP design.

## Functional requirements

1. `GET /health` mengembalikan `{status, version}` tanpa autentikasi.
2. `POST /api/v1/tickets` memvalidasi `title`, `description`, dan `reporter`.
3. `GET /api/v1/tickets` mendukung filter `status` dan `priority`.
4. `GET /api/v1/tickets/{id}` mengembalikan 404 terstruktur bila tidak ada.
5. `POST /api/v1/tickets/{id}/triage` menghasilkan output terstruktur yang divalidasi Pydantic.
6. Ticket baru berstatus `open`; triage memindahkannya ke `in_progress`.
7. Transisi `in_progress → resolved` disediakan di domain validation untuk evolusi berikutnya.

## Triage contract

Input adapter: title, description, reporter.

Output adapter:

- `category`
- `priority`
- `summary`
- `confidence` antara 0 dan 1
- `reasoning_code`

Output divalidasi sebelum disimpan. Default adalah `DeterministicTriageAdapter`; provider nyata belum digunakan.

## Persistence

SQLite melalui SQLAlchemy 2. Ticket dan triage fields disimpan pada satu tabel sederhana untuk pilot. Database dibuat saat application factory dibuat. Migration framework belum diperlukan untuk MVP single-file schema.

## Error behavior

Ticket tidak ditemukan selalu memakai HTTP 404 dengan:

```json
{"detail":{"code":"not_found","message":"Ticket not found"}}
```

Input invalid memakai HTTP 422 dari FastAPI/Pydantic.

## Security assumptions

Aplikasi hanya internal pilot dan belum memiliki authentication. Jangan expose ke jaringan publik. Reporter dan description diperlakukan sebagai untrusted input; tidak ada evaluasi HTML, template execution, shell execution, atau outbound provider call.

## Acceptance criteria

- Unit, integration, API/e2e, negative, dan golden evaluation tests pass.
- Coverage minimal 80%.
- `ruff`, `mypy`, package build, OpenAPI contract, dan template checks pass.
- No secret, no provider SDK, no production deployment.
