# Food Review Backend

Phase 1 FastAPI backend foundation for a food-item-first review platform.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
```

Update `DATABASE_URL` in `.env`, then run:

```powershell
alembic upgrade head
python -m scripts.seed
fastapi dev app/main.py
```

Health check:

```text
GET /health
```

