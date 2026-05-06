# Single-stage Dockerfile — keeps the image build deterministic on Railway.
# Why no apt-get: `psycopg[binary]` ships with libpq bundled, so we don't need
# `libpq5` / `libpq-dev` from Debian repos. Avoiding apt-get also dodges the
# transient mirror failures we saw on Railway's runner.
FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_SETTINGS_MODULE=trustgive.settings.production \
    PORT=8000

WORKDIR /app

# Copy requirements first — Docker layer cache hits when only app code changes
COPY backend/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Copy the rest of the backend
COPY backend/ /app/

EXPOSE 8000

# Migrations + static collection + gunicorn on container start.
# Railway has its own healthcheck (railway.json -> healthcheckPath /api/health/)
# so we don't ship a Dockerfile-level HEALTHCHECK that would also need curl.
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && exec gunicorn trustgive.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --access-logfile - --error-logfile -"]
