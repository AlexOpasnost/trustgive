# 04 — Local setup

## Prerequisites

| Tool | Version | Why |
|---|---|---|
| Python | 3.13 | Backend runtime |
| Node.js | 20+ | Frontend toolchain |
| Docker | any recent | Postgres in a container is the easiest path |
| Git | any | Version control |

## Repository

```bash
git clone https://github.com/AlexOpasnost/trustgive.git
cd trustgive
```

## Step 1 — Postgres

The simplest path is Docker:

```bash
docker run -d --name trustgive-pg \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=trustgive \
  -p 5432:5432 \
  postgres:17
```

Postgres 17 is required for the JSONB + GIN + pg_trgm + unaccent extensions used by ADR-005.

## Step 2 — Backend

```bash
cd backend
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

# Copy env template
cp ../.env.example .env

# Edit .env — minimum required:
#   DJANGO_SECRET_KEY=<generate via: python -c "import secrets; print(secrets.token_urlsafe(50))">
#   DATABASE_URL=postgres://postgres:postgres@localhost:5432/trustgive
#   DJANGO_DEBUG=True

# Run migrations
python manage.py makemigrations charities ingestion events i18n_app
python manage.py migrate

# Create a superuser for /admin/
python manage.py createsuperuser

# (Optional) ingest one charity to test
python manage.py ingest_propublica --ein=271661997   # GiveDirectly

# Start the dev server
python manage.py runserver
```

Visit:
- http://localhost:8000/api/health/ — should return 200 with `{"status":"ok","db":"ok"}`
- http://localhost:8000/api/docs/ — Swagger UI
- http://localhost:8000/admin/ — Django admin

## Step 3 — Frontend

In a separate terminal:

```bash
cd frontend/web
cp .env.example .env.local
# Default VITE_API_BASE_URL=http://localhost:8000 works out of the box

npm install
npm run dev
```

Visit:
- http://localhost:5173/ — homepage
- http://localhost:5173/charities — catalog (will show error if backend not running)
- http://localhost:5173/methodology — methodology page

## Step 4 — Run tests

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend/web
npm test
```

### End-to-end (requires both backend + frontend running)
```bash
cd e2e
npm install
npm run install:browsers   # one-time chromium download
npm test
```

## Step 5 — Common dev workflow

| What | Command |
|---|---|
| Regenerate TS API client from running backend | `cd frontend/web && npm run gen-api` |
| Validate OpenAPI round-trips | `cd backend && python manage.py spectacular --validate --fail-on-warn` |
| Apply translation overlay | `cd backend && python manage.py load_overlay apps/i18n/templates/ru.yaml ru` |
| Lint backend | `cd backend && ruff check .` |
| Lint frontend | `cd frontend/web && npm run lint` |
| Type-check frontend | `cd frontend/web && npm run typecheck` |

## Troubleshooting

**`makemigrations` reports `App 'i18n' could not be found in INSTALLED_APPS`** — use the app label `i18n_app` (per KB-BACKEND-TRUSTGIVE-006):
```bash
python manage.py makemigrations i18n_app
```

**`psycopg.OperationalError: connection refused`** — Postgres container not running:
```bash
docker ps                # check if trustgive-pg is up
docker start trustgive-pg
```

**Frontend `npm install` fails with peer-dep conflict** — React 19 + lib mismatch:
```bash
npm install --legacy-peer-deps
```

**Cyrillic doesn't render** — Google Fonts CDN blocked? Set `VITE_API_BASE_URL` to your backend if it's elsewhere; the font load itself comes from `fonts.googleapis.com`. If your network blocks Google Fonts, self-host them in `frontend/web/public/fonts/` and update `index.html`.

**`pg_trgm` extension permission denied** — your Postgres user needs `CREATE EXTENSION` privileges:
```bash
docker exec -it trustgive-pg psql -U postgres -c "ALTER USER postgres SUPERUSER;"
```
