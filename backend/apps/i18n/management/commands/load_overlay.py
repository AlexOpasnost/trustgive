"""Bulk-load RU translations from a YAML file into Charity / Cause / TrustBadge JSONB fields.

Format:
    charities.charity:
      "givedirectly":
        tagline: "Денежные переводы людям в условиях крайней бедности"
        description: "GiveDirectly направляет..."
    charities.cause:
      "animals":
        name: "Животные"
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Load RU/EN translation overlay from YAML into LocalizedTextField JSONB fields."

    def add_arguments(self, parser) -> None:
        parser.add_argument("path", help="Path to YAML overlay file")
        parser.add_argument("lang", choices=["en", "ru"], help="Target language key")

    def handle(self, *args: Any, **options: Any) -> None:
        path = Path(options["path"])
        if not path.exists():
            raise CommandError(f"File not found: {path}")
        lang = options["lang"]

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        applied = 0

        with transaction.atomic():
            for model_label, instances in (data or {}).items():
                model = apps.get_model(model_label)
                for slug_or_id, fields in (instances or {}).items():
                    obj = self._lookup(model, slug_or_id)
                    if obj is None:
                        self.stderr.write(self.style.WARNING(f"Skipping {model_label}/{slug_or_id}: not found"))
                        continue
                    for field_name, value in fields.items():
                        current = dict(getattr(obj, field_name) or {})
                        current[lang] = value
                        current.setdefault("en", "")
                        current.setdefault("ru", "")
                        setattr(obj, field_name, current)
                        applied += 1
                    obj.save()

        self.stdout.write(self.style.SUCCESS(f"Applied {applied} translations from {path} (lang={lang})"))

    def _lookup(self, model, slug_or_id):
        if hasattr(model, "slug"):
            return model.objects.filter(slug=slug_or_id).first()
        return model.objects.filter(pk=slug_or_id).first()
