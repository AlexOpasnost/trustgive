"""Third attempt at fixing GiveDirectly's empty LocalizedTextField columns.

Migration 0005 used `charity.save()` — donation_url persisted, JSONB fields
did not. Migration 0006 used `schema_editor.execute()` raw SQL with %s::jsonb
casts — JSONB fields still did not persist.

This migration uses the queryset `.update()` path through the historical
model, which is the same path that successfully cleared
Financial.objects.filter(...).update(...) in migration 0005. If even this
doesn't land, we have a deeper issue (which the new debug endpoint
/api/_debug/givedirectly-raw/ should expose).

Idempotent + safe.
"""
from __future__ import annotations

from django.db import migrations


GIVEDIRECTLY_REGISTRATION_ID = "271661997"


NAME = {"en": "GIVEDIRECTLY, INC.", "ru": "GiveDirectly"}

TAGLINE = {
    "en": "Cash transfers to people living in extreme poverty",
    "ru": "Денежные переводы людям в крайней бедности",
}

DESCRIPTION = {
    "en": (
        "GiveDirectly is a nonprofit that delivers cash transfers "
        "directly to people living in extreme poverty, primarily in "
        "East Africa. Recipients decide how to spend the money "
        "themselves — research shows this approach significantly "
        "improves welfare without dependency."
    ),
    "ru": (
        "GiveDirectly — некоммерческая организация, которая "
        "переводит деньги напрямую людям, живущим в крайней "
        "бедности, главным образом в Восточной Африке. "
        "Получатели сами решают, как тратить деньги — "
        "исследования показывают что такой подход значительно "
        "улучшает благосостояние без формирования зависимости."
    ),
}

METHODOLOGY_NOTE = {
    "en": (
        "This charity is verified because it is registered with "
        "the IRS as a 501(c)(3) (verified via ProPublica), has "
        "filed Form 990 in the last 24 months, and we link "
        "directly to that filing."
    ),
    "ru": (
        "Организация подтверждена: зарегистрирована как 501(c)(3) "
        "в IRS, сдала форму 990 в последние 24 месяца, и мы "
        "напрямую связываемся с этой подачей."
    ),
}


def forwards(apps, schema_editor):
    Charity = apps.get_model("charities", "Charity")
    updated = Charity.objects.filter(
        registration_id=GIVEDIRECTLY_REGISTRATION_ID
    ).update(
        name=NAME,
        tagline=TAGLINE,
        description=DESCRIPTION,
        methodology_note=METHODOLOGY_NOTE,
    )
    # Migrations don't have access to logging easily, but print goes to
    # Railway deploy logs which is what we want for forensics.
    print(f"[migration 0007] updated rows: {updated}")


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0006_fix_givedirectly_localized"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards, elidable=True),
    ]
