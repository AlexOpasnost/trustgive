"""Remove EINs from curated prose when they contradict the verified record.

27 US charities carried an EIN inside their description that disagreed with the
`registration_id` verified against ProPublica — e.g. Sesame Workshop's record says
13-2655731 while its prose asserted "EIN 13-1973898". These prose identifiers were
written at seed time and never reconciled when `fix_us_eins` later corrected the
record from the registry.

A wrong government identifier presented as fact is the most damaging possible
defect for a site whose promise is "check the source yourself": a reader who
verifies one number against the other finds the page contradicting itself.

Approach: strip the contradicting identifier rather than rewrite it. The verified
EIN is already displayed authoritatively in the identity strip, so the prose does
not need to repeat it, and deleting a false claim is safer than editing curated
copy to insert a new one. A prose EIN that MATCHES the record is left untouched.

    python manage.py strip_false_eins --dry-run
    python manage.py strip_false_eins
"""

from __future__ import annotations

import re
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.charities.models import Charity

# "EIN 02-0599710, " / "EIN 020599710; " — the identifier plus its trailing
# separator, so the surrounding sentence still reads correctly once removed.
EIN_CLAUSE = re.compile(r"EIN\s*(\d{2})-?(\d{7})\s*[,;]?\s*")
ANY_EIN = re.compile(r"\b(\d{2})-?(\d{7})\b")
FIELDS = ("description", "methodology_note")
LANGS = ("en", "ru")


def _normalise(a: str, b: str) -> str:
    return (a + b).zfill(9)


def _clean(text: str, stored: str) -> tuple[str, bool]:
    """Drop EIN clauses that disagree with `stored`. Returns (text, changed)."""
    changed = False

    def repl(m: re.Match[str]) -> str:
        nonlocal changed
        if _normalise(m.group(1), m.group(2)) == stored:
            return m.group(0)  # correct identifier — keep it
        changed = True
        return ""

    out = EIN_CLAUSE.sub(repl, text)
    if not changed:
        return text, False

    # Tidy what the removal can leave behind: "()" or "( founded 1968)".
    out = re.sub(r"\(\s*\)", "", out)
    out = re.sub(r"\(\s+", "(", out)
    out = re.sub(r"\s{2,}", " ", out)
    out = re.sub(r"\s+([,.;])", r"\1", out)
    return out.strip(), True


class Command(BaseCommand):
    help = "Strip EINs from curated prose where they contradict the verified registration_id."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args: Any, **options: Any) -> None:
        dry: bool = options["dry_run"]
        touched = leftover = 0

        with transaction.atomic():
            for c in Charity.objects.filter(country="US").order_by("slug"):
                stored = re.sub(r"\D", "", c.registration_id or "").zfill(9)
                if len(stored) != 9:
                    continue

                fields_changed: list[str] = []
                for field in FIELDS:
                    blob = getattr(c, field) or {}
                    if not isinstance(blob, dict):
                        continue
                    new_blob = dict(blob)
                    field_changed = False
                    for lang in LANGS:
                        text = new_blob.get(lang) or ""
                        if not text:
                            continue
                        cleaned, changed = _clean(text, stored)
                        if changed:
                            new_blob[lang] = cleaned
                            field_changed = True
                    if field_changed:
                        setattr(c, field, new_blob)
                        fields_changed.append(field)

                if not fields_changed:
                    continue

                touched += 1
                self.stdout.write(
                    f"[CLEAN] {c.slug} -- {', '.join(fields_changed)} (record {stored})"
                )

                # Report any contradicting EIN the clause pattern could not reach,
                # so nothing false is left behind silently.
                for field in fields_changed:
                    for lang in LANGS:
                        txt = (getattr(c, field) or {}).get(lang) or ""
                        for m in ANY_EIN.finditer(txt):
                            if _normalise(m.group(1), m.group(2)) != stored:
                                leftover += 1
                                self.stdout.write(
                                    f"        !! residual EIN {m.group(0)} "
                                    f"in {field}.{lang} — review"
                                )

                if not dry:
                    c.save(update_fields=[*fields_changed, "updated_at"])

            if dry:
                transaction.set_rollback(True)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone ({'dry' if dry else 'applied'}). "
                f"charities_cleaned={touched} residual_flags={leftover}"
            )
        )
