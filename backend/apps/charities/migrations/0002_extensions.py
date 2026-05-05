"""Enable Postgres extensions: pg_trgm (fuzzy search + ETL dedup) and unaccent (FTS).

Per ADR-001 + ADR-005. Reverse drops them — note: dropping pg_trgm will fail if any
GIN gin_trgm_ops indexes still reference it; reverse 0004 first.
"""
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="CREATE EXTENSION IF NOT EXISTS pg_trgm;",
            reverse_sql="DROP EXTENSION IF EXISTS pg_trgm;",
        ),
        migrations.RunSQL(
            sql="CREATE EXTENSION IF NOT EXISTS unaccent;",
            reverse_sql="DROP EXTENSION IF EXISTS unaccent;",
        ),
    ]
