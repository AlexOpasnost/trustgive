"""Hub sections — crawlable entry points into the catalogue (v3.21).

Why this module exists
----------------------
Search Console reported 640 URLs as "Discovered — currently not indexed" on
2026-07-31. Google knew about every charity page from the sitemap but was not
crawling them, because a sitemap line is not a vote of importance: the catalogue
renders 60 cards and loads the rest behind a "Load more" button, so only 60 of
370 charities were reachable by following links. The remaining 310 had zero
internal links pointing at them.

Hubs fix that by giving every charity several plain `<a href>` paths from the
catalogue: one per country, one per cause tag it carries, one per registry that
published its evidence.

    /charities/country/{code}      e.g. /charities/country/us
    /charities/cause/{slug}        e.g. /charities/cause/global-health
    /charities/registry/{slug}     e.g. /charities/registry/irs-990

Threshold
---------
A hub is published only when it holds **at least MIN_HUB_SIZE charities**. A page
listing one or two organisations is a thin page: it competes with the catalogue
for the same query, carries almost no link value, and is exactly what Google
declines to index. Below the threshold the grouping still exists in the data —
it just doesn't get a URL. This is why Italy (4 charities) has no country hub
while Spain (6) does.

Counts are computed against the published (verified-only) queryset, so a hub can
appear or disappear as verification coverage changes. Nothing here is hardcoded
except the registry definitions, which describe real publishers rather than data.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, TypedDict
from urllib.parse import urlparse

from apps.charities.models import Cause, Charity, Country, VerificationStatus

# A hub needs this many charities before it gets a URL. See module docstring.
MIN_HUB_SIZE = 5

# Mirrors views.PUBLISHED. Imported there rather than here to avoid a circular
# import (views imports this module).
_PUBLISHED = {"verification_status": VerificationStatus.VERIFIED}


class HubItem(TypedDict, total=False):
    kind: str
    slug: str
    label: dict[str, str]
    count: int
    path: str
    # country hubs only
    code: str
    # registry hubs only
    publisher: str
    host: str
    country: str
    description: dict[str, str]


# --------------------------------------------------------------------------- #
# Countries
# --------------------------------------------------------------------------- #

# Russian display names for Country.choices. The English side comes from the
# model's own labels, so only the RU overlay lives here.
COUNTRY_NAME_RU: dict[str, str] = {
    "US": "США",
    "GB": "Великобритания",
    "RU": "Россия",
    "CA": "Канада",
    "AU": "Австралия",
    "NL": "Нидерланды",
    "NZ": "Новая Зеландия",
    "DE": "Германия",
    "CH": "Швейцария",
    "SE": "Швеция",
    "FR": "Франция",
    "JP": "Япония",
    "SG": "Сингапур",
    "KE": "Кения",
    "ZA": "ЮАР",
    "GH": "Гана",
    "MZ": "Мозамбик",
    "LS": "Лесото",
    "SN": "Сенегал",
    "TZ": "Танзания",
    "UG": "Уганда",
    "IN": "Индия",
    "PH": "Филиппины",
    "ID": "Индонезия",
    "VN": "Вьетнам",
    "TH": "Таиланд",
    "BD": "Бангладеш",
    "BR": "Бразилия",
    "AR": "Аргентина",
    "CL": "Чили",
    "CO": "Колумбия",
    "MX": "Мексика",
    "EC": "Эквадор",
    "CR": "Коста-Рика",
    "PE": "Перу",
    "LB": "Ливан",
    "EG": "Египет",
    "JO": "Иордания",
    "TN": "Тунис",
    "IT": "Италия",
    "ES": "Испания",
    "IE": "Ирландия",
    "NO": "Норвегия",
    "BE": "Бельгия",
    "DK": "Дания",
    "PL": "Польша",
    "FI": "Финляндия",
    "AT": "Австрия",
    "IL": "Израиль",
}


# --------------------------------------------------------------------------- #
# Registries
# --------------------------------------------------------------------------- #

# A registry hub groups charities by *who published the evidence*, which is the
# only grouping that matches TrustGive's promise. It is keyed on the source
# document's URL host rather than on `SourceDocument.kind`: kind turned out to be
# inconsistent for the same publisher (71 UK charities carry `annual_report` and
# 6 carry `charity_commission_filing`, all pointing at the same Charity
# Commission register), whereas the host is exactly "which registry served this
# document".
#
# Only publishers that clear MIN_HUB_SIZE are listed. Self-published annual
# reports (one org, one domain) never form a hub, which is correct — an
# organisation's own PDF is not a registry.
REGISTRY_DEFS: list[dict[str, Any]] = [
    {
        "slug": "irs-990",
        "host": "projects.propublica.org",
        "country": "US",
        "label": {"en": "IRS Form 990", "ru": "Форма IRS 990"},
        "publisher": "ProPublica Nonprofit Explorer",
        "description": {
            "en": (
                "Organisations whose evidence is an IRS Form 990 — the annual "
                "return every US 501(c)(3) must file — served from ProPublica's "
                "mirror of the IRS release."
            ),
            "ru": (
                "Организации, чьё подтверждение — форма IRS 990, обязательная "
                "годовая отчётность американских 501(c)(3). Документы отдаются "
                "из зеркала ProPublica."
            ),
        },
    },
    {
        "slug": "uk-charity-commission",
        "host": "register-of-charities.charitycommission.gov.uk",
        "country": "GB",
        "label": {
            "en": "UK Charity Commission",
            "ru": "Комиссия по благотворительности Великобритании",
        },
        "publisher": "Charity Commission for England and Wales",
        "description": {
            "en": (
                "Organisations on the statutory register of charities for England "
                "and Wales, linked to the accounts filed against their "
                "registration number."
            ),
            "ru": (
                "Организации из государственного реестра благотворительных "
                "организаций Англии и Уэльса. Для каждой — ссылка на отчётность, "
                "поданную под её регистрационным номером."
            ),
        },
    },
    {
        "slug": "acnc-australia",
        "host": "abr.business.gov.au",
        "country": "AU",
        "label": {
            "en": "Australian Business Register / ACNC",
            "ru": "Реестр ACNC (Австралия)",
        },
        "publisher": "Australian Charities and Not-for-profits Commission",
        "description": {
            "en": (
                "Australian charities matched to their Australian Business "
                "Register record, which carries the ACNC registration status."
            ),
            "ru": (
                "Австралийские организации, сопоставленные по записи в "
                "Австралийском бизнес-реестре, где указан статус регистрации ACNC."
            ),
        },
    },
]

REGISTRY_BY_SLUG: dict[str, dict[str, Any]] = {r["slug"]: r for r in REGISTRY_DEFS}


def registry_host(slug: str) -> str | None:
    """Host of the registry with this slug, or None if the slug is unknown."""
    entry = REGISTRY_BY_SLUG.get(slug)
    return entry["host"] if entry else None


# --------------------------------------------------------------------------- #
# Count queries
# --------------------------------------------------------------------------- #


def _published():
    return Charity.objects.filter(**_PUBLISHED)


def country_hubs(min_size: int = MIN_HUB_SIZE) -> list[HubItem]:
    """Country hubs, largest first. Slug is the ISO code lowercased."""
    counts = Counter(_published().values_list("country", flat=True))
    labels = dict(Country.choices)
    items: list[HubItem] = []
    for code, count in counts.most_common():
        if count < min_size or not code:
            continue
        slug = code.lower()
        items.append(
            {
                "kind": "country",
                "slug": slug,
                "code": code,
                "label": {
                    "en": labels.get(code, code),
                    "ru": COUNTRY_NAME_RU.get(code, labels.get(code, code)),
                },
                "count": count,
                "path": f"/charities/country/{slug}",
            }
        )
    return items


def cause_hubs(min_size: int = MIN_HUB_SIZE) -> list[HubItem]:
    """Cause hubs, largest first.

    `cause_tags` is an ArrayField of slugs, so the counting is done in Python
    over the published rows (370 of them — a single indexed column read). The
    display label comes from the Cause taxonomy table, which carries EN+RU; a
    tag with no taxonomy row falls back to a de-slugified name rather than being
    dropped, so a new tag can never silently vanish from the hub index.
    """
    counter: Counter[str] = Counter()
    for tags in _published().values_list("cause_tags", flat=True):
        counter.update(t for t in (tags or []) if t)

    eligible = {slug for slug, n in counter.items() if n >= min_size}
    names = dict(Cause.objects.filter(slug__in=eligible).values_list("slug", "name"))

    items: list[HubItem] = []
    for slug, count in counter.most_common():
        if slug not in eligible:
            continue
        name = names.get(slug) or {}
        fallback = slug.replace("-", " ").capitalize()
        items.append(
            {
                "kind": "cause",
                "slug": slug,
                "label": {
                    "en": name.get("en") or fallback,
                    "ru": name.get("ru") or name.get("en") or fallback,
                },
                "count": count,
                "path": f"/charities/cause/{slug}",
            }
        )
    return items


def registry_hubs(min_size: int = MIN_HUB_SIZE) -> list[HubItem]:
    """Registry hubs, largest first.

    Counted by URL host in Python rather than with a `url__icontains` query per
    registry: one pass over the (charity, url) pairs is cheaper than N distinct
    counts, and — more importantly — `icontains` on a URL would also match a
    host appearing in a path or query string.
    """
    hosts = {r["host"]: r for r in REGISTRY_DEFS}
    per_host: dict[str, set[str]] = {h: set() for h in hosts}
    rows = Charity.objects.filter(**_PUBLISHED).values_list("slug", "source_documents__url")
    for charity_slug, url in rows:
        if not url:
            continue
        host = urlparse(url).netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        if host in per_host:
            per_host[host].add(charity_slug)

    items: list[HubItem] = []
    for host, slugs in sorted(per_host.items(), key=lambda kv: -len(kv[1])):
        count = len(slugs)
        if count < min_size:
            continue
        entry = hosts[host]
        items.append(
            {
                "kind": "registry",
                "slug": entry["slug"],
                "label": entry["label"],
                "description": entry["description"],
                "publisher": entry["publisher"],
                "host": host,
                "country": entry["country"],
                "count": count,
                "path": f"/charities/registry/{entry['slug']}",
            }
        )
    return items


def all_hubs(min_size: int = MIN_HUB_SIZE) -> dict[str, Any]:
    """Full hub index — the payload behind `GET /api/hubs/`."""
    return {
        "min_size": min_size,
        "countries": country_hubs(min_size),
        "causes": cause_hubs(min_size),
        "registries": registry_hubs(min_size),
    }
