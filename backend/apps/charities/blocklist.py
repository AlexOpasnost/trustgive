"""Legal compliance blocklist for TrustGive.

The platform operator is based in Russia. Russian law restricts publishing of:
  - Organizations classified as foreign agents (ФЗ-272)
  - Organizations classified as extremist or undesirable (Минюст РФ register)
  - Organizations providing material assistance to parties of active armed conflicts

This module captures BOTH structural (cause-tag, keyword, country) blocks and
specific (EIN/registration_id) blocks. Filters apply at TWO layers:

  1. ETL ingestion — `ingest_*` commands skip matching records before insert.
  2. Read API — `CharityViewSet.get_queryset()` excludes any record that slipped
     through (defensive double-check; see apps/charities/views.py).

Cleanup of already-loaded data: run
    python manage.py apply_blocklist [--dry-run]

This module is NOT secret; it ships in the public repo because the rules need
to be auditable. Specific EIN entries we choose to suppress are kept short and
documented case-by-case below.

Updates: when Russia's foreign-agent / extremist / undesirable registers update,
re-import lists via `python manage.py refresh_official_blocklists` (see TODO §3
of the file `apply_blocklist.py`).
"""
from __future__ import annotations

import re
from dataclasses import dataclass


# --- 1. Country block (we never ingest these) -------------------------------
# Operating from Russia, ingesting Ukrainian-registered charities is a direct
# legal risk regardless of the work they do. Filtered at ETL.
BLOCKED_COUNTRIES: set[str] = {"UA"}


# --- 2. Cause-tag block -----------------------------------------------------
# Cause taxonomy slugs (from Every.org or our overlay) that we never publish.
BLOCKED_CAUSE_TAGS: set[str] = {
    "ukraine",
    "ukraine-war",
    "ukraine-relief",
    "ukrainian-military-aid",
    "military-aid",
    "war-relief",
    "armed-forces",
    "russian-opposition",
    "russian-foreign-agents",
    # LGBTQ+ Russian-specific advocacy (banned by Russian Supreme Court 2023)
    # We still allow non-Russian LGBTQ+ charities; cause tag below is reserved
    # for charities that explicitly target the Russian context.
    "lgbtq-russia",
}


# --- 3. Keyword block (case-insensitive substring on name + description) ----
BLOCKED_KEYWORDS: list[str] = [
    # Ukrainian war relief / military
    "ukrainian armed forces",
    "ukrainian military",
    "ukraine military aid",
    "armed forces of ukraine",
    "come back alive",
    "razom for ukraine",
    "united24",
    "army sos",
    "kyiv military",
    "ukrainian frontline",
    "azov",
    # Russian banned organizations
    "anti-corruption foundation",
    "navalny",
    "fbk",
    "bellingcat",
    "memorial society",
    "open russia foundation",
    "free russia foundation",
    "ovd-info",
    "ovd info",
    # Sanctioned support / specific war causes
    "war in ukraine",
    "russia-ukraine war",
]


# --- 4. Specific registration_id (EIN / Charity Number) blocks --------------
# Maintained as a code-level list. When unsure, prefer keyword/cause block
# since structural rules age better than per-EIN entries.
BLOCKED_REGISTRATION_IDS: set[str] = {
    # Razom for Ukraine — US 501(c)(3) explicit war relief.
    "454604398",
    # Add more as identified during ingestion review (cleaned to digits-only).
}


# --- Compiled regex of keywords for fast matching ---------------------------
_KEYWORD_RE: re.Pattern[str] = re.compile(
    "|".join(re.escape(kw) for kw in BLOCKED_KEYWORDS),
    re.IGNORECASE,
)


@dataclass(frozen=True)
class BlockReason:
    rule: str  # one of: country / cause / keyword / registration_id
    detail: str

    def __str__(self) -> str:
        return f"{self.rule}: {self.detail}"


def _clean_id(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\D", "", value)


def is_blocked(
    *,
    country: str | None = None,
    registration_id: str | None = None,
    cause_tags: list[str] | None = None,
    name: str | None = None,
    description: str | None = None,
) -> BlockReason | None:
    """Return a BlockReason if any rule fires, else None.

    Order matters — country/registration are cheapest, keyword search runs last.
    """
    if country and country.upper() in BLOCKED_COUNTRIES:
        return BlockReason("country", country.upper())

    cleaned_id = _clean_id(registration_id)
    if cleaned_id and cleaned_id in BLOCKED_REGISTRATION_IDS:
        return BlockReason("registration_id", cleaned_id)

    if cause_tags:
        for tag in cause_tags:
            if tag in BLOCKED_CAUSE_TAGS:
                return BlockReason("cause", tag)

    haystack = " ".join(filter(None, [name, description])).lower()
    if haystack:
        match = _KEYWORD_RE.search(haystack)
        if match:
            return BlockReason("keyword", match.group(0))

    return None
