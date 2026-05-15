"""Test settings — for pytest only.

The earlier pytest run pointed `DJANGO_SETTINGS_MODULE` at `development`,
which inherits `DATABASE_URL` from the environment. When run via
`railway run pytest`, that env var was the LIVE Neon production database
— pytest-django tried to apply all migrations on top of the real 541
charities and crashed on a duplicate-slug constraint.

This module:
  - reads `TEST_DATABASE_URL` instead of `DATABASE_URL` (default points at
    the throwaway Postgres in docker-compose.test.yml on localhost:5433);
  - disables cachalot so tests see fresh DB state every assertion;
  - swaps in the unsalted-MD5 password hasher so any account-creation
    fixtures finish in <1 ms instead of paying Argon2 cost per call.

Postgres-specific features the app uses (FTS, pg_trgm, unaccent, JSONB)
all work on a real Postgres, so SQLite is not an option — hence the
docker-compose.test.yml sidecar.
"""
from __future__ import annotations

import environ

from .base import *  # noqa: F401,F403

_env = environ.Env()

DEBUG = False
ALLOWED_HOSTS = ["*"]

# Point at the throwaway Postgres. Default works out-of-the-box with the
# docker-compose.test.yml sidecar; override with TEST_DATABASE_URL if you
# point pytest at a Neon test branch or another Postgres.
DATABASES = {
    "default": _env.db(
        "TEST_DATABASE_URL",
        default="postgres://trustgive:trustgive@localhost:5433/trustgive_test",
    ),
}
# Reassigning DATABASES drops base.py's CONN_MAX_AGE=300, so set it back.
# CONN_MAX_AGE=0 (default when missing) closes the connection at the end of
# every request, which inside a pytest-django @django_db wrapper breaks
# multi-request tests (api_client.get() in a loop) — the next request can't
# reach the rolled-back transaction.
DATABASES["default"]["CONN_MAX_AGE"] = 300

# Cachalot caches queryset results in-process. In tests that mutate the DB
# inside a single Python process, that cache lies — turn it off.
CACHALOT_ENABLED = False

# Fast password hashing: tests don't need real cost.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Sentry must not phone home from tests even if a DSN leaks in via env.
SENTRY_DSN = ""

# Quiet down logging during tests — the JSON logger spams every request.
import logging  # noqa: E402

logging.disable(logging.CRITICAL)
