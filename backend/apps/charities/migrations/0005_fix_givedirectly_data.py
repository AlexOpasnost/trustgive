"""One-shot data correction for the GiveDirectly demo record.

Runs on the next Railway deploy. Equivalent of the `fix_givedirectly`
management command (apps/charities/management/commands/fix_givedirectly.py)
but as a migration so we don't need to invoke a CLI command on the live
container.

Two issues this fixes:

1. Charity was created with an empty `name` (early ingest run pre-dating
   the `_find_or_create` name-refresh fix). UI was falling back to slug
   (`givedirectly-inc`) which looks broken.

2. Financial row had populated `program_expenses_usd` and
   `fundraising_expenses_usd` from a pre-fix Form 990 mapping
   (`totliabend` was being mapped to fundraising — `totliabend` is total
   LIABILITIES, not fundraising expense). Showing 56.8% "Привлечение
   средств" makes the product look untrustworthy.

Idempotent — re-running has no effect (the migration framework only runs
each migration once per database, but the operations themselves are also
idempotent).

Forward-compat: once GiveDirectly is properly re-ingested with the
corrected ETL field mapping (REVIEW H-002), this fix is harmless — the
ingest will just overwrite our manual values with whatever it computes,
which by then will be correct.
"""
from __future__ import annotations

from django.db import migrations


GIVEDIRECTLY_REGISTRATION_ID = "271661997"


def fix_givedirectly_forwards(apps, schema_editor):
    Charity = apps.get_model("charities", "Charity")
    Financial = apps.get_model("charities", "Financial")

    charity = Charity.objects.filter(
        registration_id=GIVEDIRECTLY_REGISTRATION_ID
    ).first()
    if charity is None:
        # Not ingested yet on this environment — skip.
        return

    charity.name = {"en": "GIVEDIRECTLY, INC.", "ru": "GiveDirectly"}
    charity.tagline = {
        "en": "Cash transfers to people living in extreme poverty",
        "ru": "Денежные переводы людям в крайней бедности",
    }
    charity.description = {
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
    charity.methodology_note = {
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
    charity.donation_url = "https://www.givedirectly.org/donate/"
    charity.save()

    Financial.objects.filter(charity=charity).update(
        program_expenses_usd=None,
        admin_expenses_usd=None,
        fundraising_expenses_usd=None,
    )


def fix_givedirectly_backwards(apps, schema_editor):
    # No-op: we don't want to restore the broken empty name + bogus
    # financial breakdown if this migration is unapplied. If the proper
    # ETL re-ingest happens later, it will overwrite these fields anyway.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0004_name_trgm_index"),
    ]

    operations = [
        migrations.RunPython(
            fix_givedirectly_forwards,
            fix_givedirectly_backwards,
            elidable=True,
        ),
    ]
