# TrustGive backend

Django 6 + DRF + drf-spectacular + Postgres 17.

## Quickstart (local)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp ../.env.example .env  # edit DATABASE_URL etc.
python manage.py migrate
python manage.py runserver
```

Then visit:
- http://localhost:8000/api/health/ — healthcheck
- http://localhost:8000/api/docs/ — Swagger UI
- http://localhost:8000/api/schema/ — OpenAPI YAML

## Useful commands

```bash
python manage.py spectacular --validate --fail-on-warn  # validate OpenAPI round-trip
python manage.py ingest_propublica --ein=271661997      # ingest one charity by EIN
python manage.py ingest_propublica --bootstrap --limit=1000  # initial bulk load
python manage.py load_overlay apps/i18n/templates/ru.yaml ru  # load RU translations
```

## Architecture

See `../BACKEND.md` (project root). Decisions live in `../docs/adr/ADR-001` through `ADR-008`.
