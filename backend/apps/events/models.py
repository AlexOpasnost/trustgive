"""Donation-redirect event log (mirrored to PostHog server-side per ADR-008)."""
from __future__ import annotations

import uuid

from django.db import models


class SourcePage(models.TextChoices):
    DETAIL = "detail"
    COMPARISON = "comparison"
    SEO_LANDING = "seo_landing"
    SEARCH = "search"


class DonationRedirectEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_event_id = models.UUIDField(unique=True)
    charity_slug = models.SlugField(max_length=200)
    lang = models.CharField(max_length=2, choices=[("en", "English"), ("ru", "Russian")])
    source_page = models.CharField(max_length=20, choices=SourcePage.choices, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["charity_slug", "-created_at"], name="donredir_slug_idx"),
            models.Index(fields=["-created_at"], name="donredir_created_idx"),
        ]
        ordering = ["-created_at"]
