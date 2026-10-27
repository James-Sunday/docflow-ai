# DocFlow AI

A working first vertical slice for evidence-bearing document extraction and deterministic business validation. It accepts synthetic invoice-style fields, returns typed values with confidence, page, evidence, and extraction method, and routes rule failures to review. It never auto-approves a financial record.

```bash
uv sync --extra dev
uv run pytest -q
uv run uvicorn app.main:app --reload
```

The initial extractor is deliberately deterministic. File upload, object storage, OCR, durable review persistence, workers, and Azure Document Intelligence are later upgrades and are not claimed by this version.
