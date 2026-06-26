# CampaignPilot AI - uv Setup and Slice 1 Readiness

This project uses **uv** for the Python backend dependency setup.

## 1. Install prerequisites

Required tools:

- Docker Desktop
- Node.js 22 LTS
- uv
- Git Bash / PowerShell / Terminal

## 2. Install uv

macOS/Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify:

```bash
uv --version
```

## 3. Prepare environment file

From project root:

```bash
cp .env.example backend/.env
```

For Slice 1, set at least:

```env
OPENAI_API_KEY=your_key_here
```

If you only want to test the skeleton health endpoint, the placeholder key is fine.

## 4. Backend setup with uv

```bash
cd backend
uv python install 3.11
uv sync --extra dev
uv run python --version
uv run python -m compileall app
uv run pytest
```

Expected:

```text
compileall completes without error
pytest shows all tests passed
```

Run backend:

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/api/v1/health
```

Expected response shape:

```json
{
  "success": true,
  "message": "Health check successful",
  "data": {
    "status": "ok",
    "service": "campaignpilot-api",
    "version": "0.1.0"
  },
  "error": null,
  "meta": {
    "request_id": "req_xxx",
    "timestamp": "..."
  }
}
```

## 5. Frontend setup

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

Expected:

- CampaignPilot AI heading is visible
- Skeleton page renders
- Browser console has no fatal React/Vite error

## 6. Docker setup test

From project root:

```bash
cp .env.example backend/.env

docker compose up --build
```

Check services:

```bash
docker compose ps
curl http://localhost:8000/api/v1/health
curl http://localhost:9200
```

Expected:

- backend container running
- frontend container running
- postgres container running
- elasticsearch container running
- backend health endpoint returns uniform ApiResponse envelope

## 7. Slice 1 readiness checklist

Before asking AI editor to implement Slice 1, confirm:

```bash
cd backend
uv sync --extra dev
uv run python -m compileall app
uv run pytest
```

Then confirm:

```bash
uv run uvicorn app.main:app --reload --port 8000
curl http://localhost:8000/api/v1/health
```

Also confirm these files exist:

```text
backend/pyproject.toml
backend/.python-version
backend/app/main.py
backend/app/core/response.py
backend/app/api/routes/chat_routes.py
backend/app/api/routes/campaign_routes.py
backend/app/services/chat_service.py
backend/app/services/campaign_service.py
backend/app/db/models/campaign_model.py
backend/app/db/models/campaign_brief_model.py
backend/app/db/models/conversation_message_model.py
backend/app/db/models/message_variant_model.py
backend/app/db/models/llm_trace_model.py
docs/master/01_START_SLICE_1_PROMPT.md
docs/slices/slice_01_changes.md
```

## 8. What to ask AI editor next

Use this exact file as implementation prompt:

```text
docs/master/01_START_SLICE_1_PROMPT.md
```

Ask:

```text
Implement ONLY Slice 1: Campaign Chat + Brief Extraction + Variant Generation.
Follow the folder structure strictly. Do not implement Slice 2 or later.
Use uv for backend dependencies.
Update docs/slices/slice_01_changes.md after implementation.
```

## uv.lock note

`uv sync` may create `backend/uv.lock` on your machine. Commit that file after the first successful setup so future installs are reproducible.
