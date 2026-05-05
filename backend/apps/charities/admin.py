"""Minimal Django admin — Phase 4.5 expands with custom forms for LocalizedTextField."""
from django.contrib import admin

from apps.charities.models import (
    Cause,
    Charity,
    CharitySlugAlias,
    CharityTrustBadge,
    Financial,
    NewsMention,
    SourceDocument,
    TrustBadge,
)


@admin.register(Charity)
class CharityAdmin(admin.ModelAdmin):
    list_display = ("slug", "country", "verification_status", "is_stale", "last_filed_date")
    list_filter = ("country", "verification_status", "is_stale", "ingestion_source")
    search_fields = ("slug", "registration_id")
    readonly_fields = ("id", "search_vector", "name_trgm", "created_at", "updated_at")


admin.site.register(Cause)
admin.site.register(CharitySlugAlias)
admin.site.register(Financial)
admin.site.register(SourceDocument)
admin.site.register(TrustBadge)
admin.site.register(CharityTrustBadge)
admin.site.register(NewsMention)
