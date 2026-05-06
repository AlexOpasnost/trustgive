"""Custom Django fields — LocalizedTextField for {en, ru} JSONB storage (per ADR-006)."""
from __future__ import annotations

import json
from typing import Any

from django.db import models


def _empty_localized() -> dict[str, str]:
    return {"en": "", "ru": ""}


class LocalizedTextField(models.JSONField):
    """JSONB column storing {en: str, ru: str, ...}; serialised as nested object on the wire.

    Per ADR-006: nested object pattern beats paired _en/_ru columns for schema evolution
    (adding a third language is a no-op).
    """

    description = "Bilingual text stored as JSONB {en, ru}"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("default", _empty_localized)
        super().__init__(*args, **kwargs)

    def from_db_value(self, value: Any, expression: Any, connection: Any) -> dict[str, str]:
        if value is None:
            return _empty_localized()
        # psycopg3 with Postgres returns JSONB as Python dict (auto-deserialised),
        # but some configurations / driver versions may return the JSON text instead.
        # Handle both — string is parsed as JSON, anything else degrades to default.
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (ValueError, TypeError):
                return _empty_localized()
        if isinstance(value, dict):
            value.setdefault("en", "")
            value.setdefault("ru", "")
            return value
        return _empty_localized()

    def get_prep_value(self, value: Any) -> Any:
        if value is None:
            return _empty_localized()
        if isinstance(value, dict):
            value = {**value}
            value.setdefault("en", "")
            value.setdefault("ru", "")
            return super().get_prep_value(value)
        return super().get_prep_value(value)
