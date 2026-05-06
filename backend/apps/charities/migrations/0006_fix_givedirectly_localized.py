"""Follow-up to migration 0005 — set the LocalizedTextField (JSONB) values
that didn't persist via the historical model's ORM save() in 0005.

Diagnostic: after 0005 ran on the live DB, scalar fields (donation_url) and
related-table updates (Financial.update(...)) applied correctly, but the
JSONB-backed LocalizedTextField values (name, tagline, description,
methodology_note) read back as the default `{"en":"","ru":""}`. Fastest
unblock is raw SQL — bypasses the historical ORM entirely.

Idempotent: WHERE clause keys on `registration_id`. Safe to run on any
environment; a no-op where the GiveDirectly record isn't ingested.
"""
from __future__ import annotations

import json

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
    schema_editor.execute(
        """
        UPDATE charities_charity
        SET name = %s::jsonb,
            tagline = %s::jsonb,
            description = %s::jsonb,
            methodology_note = %s::jsonb
        WHERE registration_id = %s
        """,
        params=[
            json.dumps(NAME, ensure_ascii=False),
            json.dumps(TAGLINE, ensure_ascii=False),
            json.dumps(DESCRIPTION, ensure_ascii=False),
            json.dumps(METHODOLOGY_NOTE, ensure_ascii=False),
            GIVEDIRECTLY_REGISTRATION_ID,
        ],
    )


def backwards(apps, schema_editor):
    # No-op — we don't want to restore the broken empty state.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0005_fix_givedirectly_data"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards, elidable=True),
    ]
