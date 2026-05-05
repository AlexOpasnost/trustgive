from django.apps import AppConfig


class CharitiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.charities"

    def ready(self) -> None:
        # Wire post_save signals for CDN cache invalidation
        from apps.charities import signals  # noqa: F401
