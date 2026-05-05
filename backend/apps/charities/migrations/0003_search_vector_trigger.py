"""Postgres trigger that populates Charity.search_vector AND Charity.name_trgm
in a single BEFORE INSERT/UPDATE function — atomic with row writes.

Reads JSONB localised fields via -> / ->> operators per ADR-006 (the ADR-005
reconciliation in API_SPEC.md §10).

Reverse drops trigger first, then function.
"""
from django.db import migrations


FORWARD_SQL = r"""
CREATE OR REPLACE FUNCTION trustgive_charity_searchable_update() RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('simple', unaccent(coalesce(NEW.name->>'en', ''))), 'A') ||
        setweight(to_tsvector('simple', unaccent(coalesce(NEW.name->>'ru', ''))), 'A') ||
        setweight(to_tsvector('simple', coalesce(NEW.registration_id, '')), 'B') ||
        setweight(to_tsvector('simple', unaccent(coalesce(NEW.description->>'en', ''))), 'C') ||
        setweight(to_tsvector('simple', unaccent(coalesce(NEW.description->>'ru', ''))), 'C');

    NEW.name_trgm := lower(
        coalesce(NEW.name->>'en', '') || ' ' || coalesce(NEW.name->>'ru', '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trustgive_charity_searchable_trigger ON charities_charity;
CREATE TRIGGER trustgive_charity_searchable_trigger
    BEFORE INSERT OR UPDATE OF name, description, registration_id
    ON charities_charity
    FOR EACH ROW EXECUTE FUNCTION trustgive_charity_searchable_update();
"""

REVERSE_SQL = r"""
DROP TRIGGER IF EXISTS trustgive_charity_searchable_trigger ON charities_charity;
DROP FUNCTION IF EXISTS trustgive_charity_searchable_update();
"""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0002_extensions"),
    ]

    operations = [
        migrations.RunSQL(sql=FORWARD_SQL, reverse_sql=REVERSE_SQL),
    ]
