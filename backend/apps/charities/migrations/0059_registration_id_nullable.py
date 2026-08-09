"""Let a charity have no registration number, so a false one can be removed.

`registration_id` was NOT NULL inside the `(country, registration_id)` unique
constraint, which meant exactly one row per country could hold `""`. That made
removing a *known-false* government identifier impossible beyond the first one —
the blocker on DATA_INTEGRITY Finding 11 (four New Zealand numbers registered to
other organisations) and Finding 7 (twenty-two Canadian ones).

Postgres treats NULLs as distinct in a unique index, so many rows per country
may hold NULL while real numbers stay unique.

The data step folds the one existing `""` into NULL, so "we do not know this
charity's registration" has a single representation. An empty string is a value
and collides; NULL does not.

Not reversible in a useful sense: going back to NOT NULL would require inventing
a value for every NULL, which is the thing this migration exists to stop.
"""

from django.db import migrations, models


def blank_to_null(apps, schema_editor):
    Charity = apps.get_model("charities", "Charity")
    updated = Charity.objects.filter(registration_id="").update(registration_id=None)
    if updated:
        print(f"  registration_id: {updated} empty string(s) -> NULL")


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0058_alter_charity_affiliated_charities"),
    ]

    operations = [
        migrations.AlterField(
            model_name="charity",
            name="registration_id",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.RunPython(blank_to_null, migrations.RunPython.noop),
    ]
