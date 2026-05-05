# --- Build stage ---
FROM python:3.13-slim AS build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# --- Runtime stage ---
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=trustgive.settings.production \
    PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash app

COPY --from=build /install /usr/local
WORKDIR /app
COPY --chown=app:app . /app

USER app

# Entrypoint: run migrations, collect static, start gunicorn
RUN printf '#!/bin/sh\nset -e\npython manage.py migrate --noinput\npython manage.py collectstatic --noinput\nexec gunicorn trustgive.wsgi:application --bind 0.0.0.0:${PORT} --workers 2 --access-logfile - --error-logfile -\n' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -fsS "http://localhost:${PORT}/api/health/" || exit 1

CMD ["/app/entrypoint.sh"]
