"""Note (per KB-BACKEND-TRUSTGIVE-006): Django reserves `i18n` namespace for the
translation framework. We set `label = "i18n_app"` to avoid INSTALLED_APPS resolution
collision while keeping the on-disk module path semantic (`apps/i18n/`).
"""
from django.apps import AppConfig


class I18nConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.i18n"
    label = "i18n_app"
    verbose_name = "TrustGive i18n"
