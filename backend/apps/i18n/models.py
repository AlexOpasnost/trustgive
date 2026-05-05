"""TranslationOverlay — per-instance manual translations (RU curation overlay)."""
from __future__ import annotations

from django.db import models


class TranslationOverlay(models.Model):
    """Stores curated translation strings indexed by (model, instance_id, field, lang).

    Used for the Django admin "two-input pair" UX. ETL never touches this table —
    Alex curates via admin, then a periodic apply_overlay command pushes the strings
    into the corresponding LocalizedTextField JSONB.
    """

    model_label = models.CharField(max_length=100, help_text="e.g. 'charities.charity'")
    instance_id = models.CharField(max_length=64)
    field = models.CharField(max_length=100, help_text="e.g. 'name', 'description'")
    lang = models.CharField(max_length=2, choices=[("en", "English"), ("ru", "Russian")])
    value = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["model_label", "instance_id", "field", "lang"],
                name="uniq_overlay_key",
            ),
        ]
        indexes = [
            models.Index(fields=["model_label", "instance_id"], name="overlay_lookup_idx"),
        ]
