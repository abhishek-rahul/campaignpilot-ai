# Slice 06 Changes - Evaluation + Observability + Docker

## 1. Goal

Describe the exact goal of this slice.

## 2. Implemented Backend Files

- `backend/app/...`

## 3. Implemented Frontend Files

- `frontend/src/...`

## 4. Database Changes

- Migration files added:
- Tables/entities introduced:
- Seed data added:

## 5. API Contract Changes

Mention whether the implementation follows `docs/architecture/07_API_Contract_CampaignPilot_AI_v3.docx` exactly.

## 6. Environment / Config Changes

Mention new environment variables or Docker changes.

## 7. Testing Steps

### Backend automated checks

```bash
cd backend
pytest
```

### Frontend automated checks

```bash
cd frontend
npm run build
```

### Manual testing

1. Start services using `docker compose up --build`.
2. Open backend health URL: `http://localhost:8000/api/v1/health`.
3. Open frontend URL: `http://localhost:5173`.
4. Test this slice's main happy path.
5. Test at least one validation/error case.

## 8. Test Evidence

Paste API responses, screenshots, or logs here.

## 9. Known Issues

- None yet.

## 10. Next Slice Notes

Mention anything the next slice should know.
