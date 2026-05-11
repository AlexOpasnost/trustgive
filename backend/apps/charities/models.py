"""Charity domain models. See API_SPEC.md §2 components and ADR-001 for indexing.

All localised text fields use LocalizedTextField (JSONB {en, ru}) per ADR-006.
search_vector is populated by a Postgres trigger reading via JSONB ->> operator
(ADR-005 reconciled per API_SPEC §10).
"""
from __future__ import annotations

import uuid

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models

from apps.core.fields import LocalizedTextField


class Country(models.TextChoices):
    # Original (US/UK/RU/CA/AU/NL) — strong English-speaking + Dutch regulators
    US = "US", "United States"
    GB = "GB", "United Kingdom"
    RU = "RU", "Russia"
    CA = "CA", "Canada"
    AU = "AU", "Australia"
    NL = "NL", "Netherlands"
    # v3.7a — additional regulated-geo countries (strong national charity regulators)
    NZ = "NZ", "New Zealand"
    DE = "DE", "Germany"
    CH = "CH", "Switzerland"
    SE = "SE", "Sweden"
    FR = "FR", "France"
    JP = "JP", "Japan"
    SG = "SG", "Singapore"
    # v3.7b — unregulated-geo countries (verification via org annual reports)
    # Africa
    KE = "KE", "Kenya"
    ZA = "ZA", "South Africa"
    GH = "GH", "Ghana"
    MZ = "MZ", "Mozambique"
    LS = "LS", "Lesotho"
    SN = "SN", "Senegal"
    TZ = "TZ", "Tanzania"
    UG = "UG", "Uganda"
    # South & SE Asia
    IN = "IN", "India"
    PH = "PH", "Philippines"
    ID = "ID", "Indonesia"
    VN = "VN", "Vietnam"
    TH = "TH", "Thailand"
    BD = "BD", "Bangladesh"
    # Latin America
    BR = "BR", "Brazil"
    AR = "AR", "Argentina"
    CL = "CL", "Chile"
    CO = "CO", "Colombia"
    MX = "MX", "Mexico"
    EC = "EC", "Ecuador"
    CR = "CR", "Costa Rica"
    PE = "PE", "Peru"
    # MENA
    LB = "LB", "Lebanon"
    EG = "EG", "Egypt"
    JO = "JO", "Jordan"
    TN = "TN", "Tunisia"
    # v3.10 — additional regulated EU + Ireland (Italy, Spain, Ireland, Norway)
    IT = "IT", "Italy"
    ES = "ES", "Spain"
    IE = "IE", "Ireland"
    NO = "NO", "Norway"
    # v3.11 — Belgium + Denmark
    BE = "BE", "Belgium"
    DK = "DK", "Denmark"
    # v3.14 — Poland + Finland + Austria + Israel
    PL = "PL", "Poland"
    FI = "FI", "Finland"
    AT = "AT", "Austria"
    IL = "IL", "Israel"


class SizeBucket(models.TextChoices):
    SMALL = "small", "Small (<$100K)"
    MEDIUM = "medium", "Medium ($100K-$1M)"
    LARGE = "large", "Large (>$1M)"


class VerificationStatus(models.TextChoices):
    VERIFIED = "verified", "Verified"
    LISTED = "listed", "Listed"
    STALE = "stale", "Stale"


class IngestionSource(models.TextChoices):
    PROPUBLICA = "propublica"
    EVERY_ORG = "every_org"
    CHARITYBASE = "charitybase"
    MANUAL_RU = "manual_ru"
    MANUAL_CURATION = "manual_curation"


class Bucket(models.TextChoices):
    """v3.0 emotional taxonomy — 3 top-level buckets for the homepage hero cards.

    See DESIGN.md v3.0 §A. The cause_tags ArrayField stays as fine-grained
    metadata; bucket is the user-facing primary filter.
    """

    PEOPLE = "people", "People"
    ANIMALS = "animals", "Animals"
    PLANET = "planet", "Planet"


class PhotoLicense(models.TextChoices):
    """Short license codes for hero_photo_license. Empty string when no photo.

    See DESIGN.md v3.0 §D photo policy.
    """

    CC0 = "cc0", "CC0 / Public Domain"
    CC_BY = "cc-by", "CC-BY"
    CC_BY_SA = "cc-by-sa", "CC-BY-SA"
    PRESS_KIT = "press-kit", "Press kit / media-resources"
    UNSPLASH = "unsplash", "Unsplash"
    OGL = "ogl", "Open Government License"


class Cause(models.Model):
    """Cause taxonomy seeded from Every.org's 66 categories + RU translation overlay."""

    slug = models.SlugField(unique=True, max_length=100)
    name = LocalizedTextField()
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children"
    )
    charity_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["parent"])]
        ordering = ["slug"]

    def __str__(self) -> str:
        return f"{self.slug}"


class Charity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True, max_length=200)

    name = LocalizedTextField()
    tagline = LocalizedTextField()
    description = LocalizedTextField()
    methodology_note = LocalizedTextField()
    logo_url = models.URLField(blank=True, default="")
    donation_url = models.URLField(blank=True, default="")

    # v3.0 photo-first redesign (DESIGN.md v3.0 §A, §B, §C, §D).
    # hero_photo_url is a public, hot-linkable URL to a 3:2 (or 16:9) landscape
    # photo of the charity's actual work. Empty string ⇒ frontend renders the
    # BrandedAvatar fallback (DESIGN.md §B.3, §D fallback chain).
    hero_photo_url = models.URLField(max_length=500, blank=True, default="")
    hero_photo_caption = LocalizedTextField()
    hero_photo_credit = models.CharField(max_length=200, blank=True, default="")
    hero_photo_license = models.CharField(
        max_length=20,
        choices=PhotoLicense.choices,
        blank=True,
        default="",
    )

    # v3.0 emotional taxonomy — primary filter (DESIGN.md v3.0 §A).
    # Default "people" because all v2.0 seeds are people-bucket charities;
    # migration 0011 explicitly stamps that, migration 0012 adds animals/planet.
    bucket = models.CharField(
        max_length=10,
        choices=Bucket.choices,
        default=Bucket.PEOPLE,
        db_index=True,
    )

    country = models.CharField(max_length=2, choices=Country.choices)
    registration_id = models.CharField(max_length=64)
    cause_tags = ArrayField(models.SlugField(max_length=100), default=list)

    size_bucket = models.CharField(max_length=10, choices=SizeBucket.choices, blank=True, default="")
    verification_status = models.CharField(
        max_length=10,
        choices=VerificationStatus.choices,
        default=VerificationStatus.LISTED,
    )
    is_stale = models.BooleanField(default=False)
    last_filed_date = models.DateField(null=True, blank=True)
    total_revenue_usd = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )
    program_expense_pct = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    founded_year = models.PositiveIntegerField(null=True, blank=True)

    ingestion_source = models.CharField(max_length=20, choices=IngestionSource.choices)

    # Search support — populated by Postgres trigger (apps/charities/migrations/0003_search_vector_trigger)
    search_vector = SearchVectorField(null=True, blank=True)
    name_trgm = models.CharField(max_length=600, blank=True, default="")

    affiliated_charities = models.ManyToManyField(
        "self", blank=True, symmetrical=True, related_name="affiliations"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["country", "registration_id"], name="uniq_country_registration"
            ),
        ]
        indexes = [
            models.Index(fields=["country"], name="charity_country_idx"),
            models.Index(fields=["verification_status"], name="charity_verstatus_idx"),
            models.Index(fields=["size_bucket"], name="charity_size_idx"),
            models.Index(fields=["is_stale"], name="charity_stale_idx"),
            models.Index(fields=["-last_filed_date"], name="charity_filed_desc_idx"),
            models.Index(fields=["-total_revenue_usd"], name="charity_rev_desc_idx"),
            GinIndex(fields=["cause_tags"], name="charity_causes_gin"),
            GinIndex(fields=["search_vector"], name="charity_search_gin"),
        ]
        ordering = ["-last_filed_date"]

    def __str__(self) -> str:
        return f"{self.slug} ({self.country})"


class CharitySlugAlias(models.Model):
    """Past slugs for a charity. Resolves to a 301 redirect (per API_SPEC §6)."""

    charity = models.ForeignKey(Charity, on_delete=models.CASCADE, related_name="slug_aliases")
    slug = models.SlugField(unique=True, max_length=200)
    retired_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-retired_at"]


class Financial(models.Model):
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE, related_name="financial_history")
    year = models.PositiveSmallIntegerField()
    total_revenue_usd = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    program_expenses_usd = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    admin_expenses_usd = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    fundraising_expenses_usd = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    top_executive_comp_usd = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    top_executive_name = models.CharField(max_length=200, blank=True, default="")
    source_url = models.URLField()
    source_label = models.CharField(max_length=200, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["charity", "year"], name="uniq_financial_year"),
        ]
        indexes = [
            models.Index(fields=["charity", "-year"], name="financial_charity_year_idx"),
        ]
        ordering = ["-year"]


class DocumentKind(models.TextChoices):
    IRS_990 = "irs_990", "IRS Form 990"
    IRS_990EZ = "irs_990ez", "IRS Form 990-EZ"
    IRS_990PF = "irs_990pf", "IRS Form 990-PF"
    CHARITY_COMMISSION = "charity_commission_filing", "Charity Commission Filing"
    MINJUST = "minjust_registration", "Минюст Registration"
    SONKO = "sonko_registration", "СОНКО Registration"
    AUDIT = "audit", "Independent Audit"
    STATE = "state_registration", "State Registration"
    ANNUAL_REPORT = "annual_report", "Annual Report"


class FileFormat(models.TextChoices):
    PDF = "pdf"
    HTML = "html"
    XLSX = "xlsx"
    JSON = "json"


class SourceDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE, related_name="source_documents")
    kind = models.CharField(max_length=40, choices=DocumentKind.choices)
    label = LocalizedTextField()
    url = models.URLField(max_length=500)
    filed_date = models.DateField(null=True, blank=True)
    source_label = models.CharField(max_length=200, blank=True, default="")
    file_format = models.CharField(max_length=10, choices=FileFormat.choices, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["charity", "kind"], name="srcdoc_charity_kind_idx"),
            models.Index(fields=["-filed_date"], name="srcdoc_filed_desc_idx"),
        ]
        ordering = ["-filed_date"]


class TrustBadge(models.Model):
    """Issuer-level catalog of trust badges (BBB, Charity Commission, СОНКО, etc.)."""

    slug = models.SlugField(unique=True, max_length=100)
    label = LocalizedTextField()
    image_url = models.URLField(blank=True, default="")
    issuer = models.CharField(max_length=200)
    description = LocalizedTextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["slug"]


class CharityTrustBadge(models.Model):
    """M2M-through table — per-assignment metadata (issued_date, verify_url)."""

    charity = models.ForeignKey(Charity, on_delete=models.CASCADE, related_name="charity_badges")
    badge = models.ForeignKey(TrustBadge, on_delete=models.CASCADE, related_name="charity_assignments")
    issued_date = models.DateField(null=True, blank=True)
    verify_url = models.URLField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["charity", "badge"], name="uniq_charity_badge"),
        ]
        indexes = [models.Index(fields=["badge"], name="charitybadge_badge_idx")]


class NewsMention(models.Model):
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE, related_name="news_mentions")
    url = models.URLField(max_length=500)
    publisher = models.CharField(max_length=200)
    title = models.CharField(max_length=500)
    published_date = models.DateField()
    language = models.CharField(max_length=2, choices=[("en", "English"), ("ru", "Russian")], default="en")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["charity", "-published_date"], name="news_charity_pubd_idx")]
        ordering = ["-published_date"]
