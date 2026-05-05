"""Reusable serializers and serializer fields."""
from __future__ import annotations

from typing import Any

from rest_framework import serializers


class LocalizedSerializerField(serializers.JSONField):
    """Emits {en: '', ru: ''} ensuring both keys are always present."""

    def to_representation(self, value: Any) -> dict[str, str]:
        v = value or {}
        return {"en": v.get("en", "") or "", "ru": v.get("ru", "") or ""}

    def to_internal_value(self, data: Any) -> dict[str, str]:
        if not isinstance(data, dict):
            self.fail("invalid")
        return {"en": str(data.get("en", "")), "ru": str(data.get("ru", ""))}
