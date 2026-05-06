"""One-off data correction for the GiveDirectly demo record.

Two issues to clean up:

1. The charity was created with an empty `name` (early ingest run pre-dating
   the `_find_or_create` name-refresh fix). Slug-only display in the UI looks
   broken.

2. The Financial row has populated `program_expenses_usd` and
   `fundraising_expenses_usd` that came from a pre-fix mapping (totfuncexpns
   and totliabend respectively — the latter is total LIABILITIES, not
   fundraising expense). Showing 56.8% "Привлечение средств" makes the
   product look untrustworthy.

This command is idempotent — safe to run multiple times. Removes once
GiveDirectly is properly re-ingested with the corrected ETL.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.charities.models import Charity, Financial


GIVEDIRECTLY_SLUGS = ["givedirectly-inc", "givedirectly"]


class Command(BaseCommand):
    help = "Fix GiveDirectly's empty name + bogus financial breakdown."

    def handle(self, *args, **options) -> None:
        with transaction.atomic():
            charity = (
                Charity.objects.filter(slug__in=GIVEDIRECTLY_SLUGS)
                .filter(registration_id="271661997")
                .first()
            )
            if charity is None:
                self.stdout.write(self.style.WARNING("GiveDirectly not found — skipping"))
                return

            # Update charity-level fields
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

            # Clear bogus per-category breakdown (program/admin/fundraising)
            updated = Financial.objects.filter(charity=charity).update(
                program_expenses_usd=None,
                admin_expenses_usd=None,
                fundraising_expenses_usd=None,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Fixed GiveDirectly: name={charity.name['en']!r}, "
                f"cleared {updated} Financial row(s) bogus breakdown."
            )
        )
