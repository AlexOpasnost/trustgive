"""GIN(gin_trgm_ops) index on Charity.name_trgm for typo-tolerant fuzzy search."""
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0003_search_vector_trigger"),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "CREATE INDEX IF NOT EXISTS charity_name_trgm_idx "
                "ON charities_charity USING GIN (name_trgm gin_trgm_ops);"
            ),
            reverse_sql="DROP INDEX IF EXISTS charity_name_trgm_idx;",
        ),
    ]
