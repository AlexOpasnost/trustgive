"""ETL audit + provenance models (per ADR-004)."""
from __future__ import annotations

import uuid

from django.db import models

from apps.charities.models import Charity, IngestionSource


class IngestionStatus(models.TextChoices):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    PARTIAL = "partial"
    FAILED = "failed"


class IngestionLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.CharField(max_length=20, choices=IngestionSource.choices)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=IngestionStatus.choices, default=IngestionStatus.RUNNING)
    records_seen = models.PositiveIntegerField(default=0)
    records_upserted = models.PositiveIntegerField(default=0)
    records_skipped = models.PositiveIntegerField(default=0)
    errors = models.JSONField(default=list, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["source", "-started_at"], name="ingestionlog_src_idx"),
        ]
        ordering = ["-started_at"]


class SourceMapping(models.Model):
    """Per-source provenance — same charity can be enriched by N sources."""

    charity = models.ForeignKey(Charity, on_delete=models.CASCADE, related_name="source_mappings")
    source = models.CharField(max_length=20, choices=IngestionSource.choices)
    source_id = models.CharField(max_length=200)
    last_synced_at = models.DateTimeField(auto_now=True)
    raw_data_hash = models.BinaryField(max_length=32, blank=True, default=b"")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["charity", "source"], name="uniq_charity_source"),
            models.UniqueConstraint(fields=["source", "source_id"], name="uniq_source_source_id"),
        ]
        indexes = [
            models.Index(fields=["source", "-last_synced_at"], name="srcmap_src_synced_idx"),
        ]
