"""DRF serializers for charity catalog and detail."""
from __future__ import annotations

from typing import Any

from rest_framework import serializers

from apps.charities.models import (
    Cause,
    Charity,
    CharityTrustBadge,
    Financial,
    NewsMention,
    SourceDocument,
)
from apps.core.serializers import LocalizedSerializerField


class CauseSerializer(serializers.ModelSerializer):
    name = LocalizedSerializerField()
    parent_slug = serializers.SlugRelatedField(source="parent", slug_field="slug", read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Cause
        fields = ("slug", "name", "parent_slug", "charity_count", "children")

    def get_children(self, obj: Cause) -> list[dict[str, Any]]:
        # Only render children at the top level (when parent is null)
        if obj.parent_id is not None:
            return []
        children_qs = Cause.objects.filter(parent=obj).order_by("slug")
        return CauseSerializer(children_qs, many=True).data


class TrustBadgeNestedSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(source="badge.slug")
    label = LocalizedSerializerField(source="badge.label")
    image_url = serializers.URLField(source="badge.image_url", allow_blank=True)
    issuer = serializers.CharField(source="badge.issuer")

    class Meta:
        model = CharityTrustBadge
        fields = ("slug", "label", "image_url", "issuer", "issued_date", "verify_url")


class FinancialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Financial
        fields = (
            "year",
            "total_revenue_usd",
            "program_expenses_usd",
            "admin_expenses_usd",
            "fundraising_expenses_usd",
            "top_executive_comp_usd",
            "top_executive_name",
            "source_url",
            "source_label",
        )


class SourceDocumentSerializer(serializers.ModelSerializer):
    label = LocalizedSerializerField()

    class Meta:
        model = SourceDocument
        fields = ("id", "kind", "label", "url", "filed_date", "source_label", "file_format")


class NewsMentionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsMention
        fields = ("url", "publisher", "title", "published_date", "language")


class MoneyBreakdownLineSerializer(serializers.Serializer):
    label = LocalizedSerializerField()
    amount_usd = serializers.DecimalField(max_digits=18, decimal_places=2)
    percent = serializers.DecimalField(max_digits=5, decimal_places=2)


class MoneyBreakdownSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    lines = MoneyBreakdownLineSerializer(many=True)
    source_label = serializers.CharField(allow_blank=True)
    source_document_id = serializers.UUIDField(allow_null=True)


def _money_breakdown_from_financial(charity: Charity) -> dict[str, Any] | None:
    """Compute the 'Where the money goes' payload from latest Financial row."""
    latest: Financial | None = charity.financial_history.order_by("-year").first()
    if latest is None or latest.total_revenue_usd in (None, 0):
        return None

    primary_source: SourceDocument | None = (
        charity.source_documents.filter(kind__startswith="irs_990")
        .order_by("-filed_date")
        .first()
    )

    total = float(latest.total_revenue_usd)
    lines = []

    def _push(label_en: str, label_ru: str, amount: Any) -> None:
        if amount is None:
            return
        amount_f = float(amount)
        if total == 0:
            percent = 0.0
        else:
            percent = round((amount_f / total) * 100, 2)
        lines.append(
            {
                "label": {"en": label_en, "ru": label_ru},
                "amount_usd": amount_f,
                "percent": percent,
            }
        )

    _push("Programs", "Программы", latest.program_expenses_usd)
    _push("Administration", "Администрация", latest.admin_expenses_usd)
    _push("Fundraising", "Привлечение средств", latest.fundraising_expenses_usd)

    # No usable per-category split → don't render a misleading partial breakdown.
    # Frontend's CharityDetailPage already conditionally renders the section.
    if not lines:
        return None

    return {
        "year": latest.year,
        "lines": lines,
        "source_label": latest.source_label,
        "source_document_id": str(primary_source.id) if primary_source else None,
    }


class CharitySummarySerializer(serializers.ModelSerializer):
    name = LocalizedSerializerField()
    tagline = LocalizedSerializerField()
    trust_badges = serializers.SerializerMethodField()

    class Meta:
        model = Charity
        fields = (
            "slug",
            "name",
            "tagline",
            "logo_url",
            "country",
            "registration_id",
            "cause_tags",
            "size_bucket",
            "verification_status",
            "is_stale",
            "last_filed_date",
            "total_revenue_usd",
            "program_expense_pct",
            "trust_badges",
        )

    def get_trust_badges(self, obj: Charity) -> list[dict[str, Any]]:
        return TrustBadgeNestedSerializer(obj.charity_badges.all(), many=True).data


class CharityDetailSerializer(CharitySummarySerializer):
    description = LocalizedSerializerField()
    methodology_note = LocalizedSerializerField()
    money_breakdown = serializers.SerializerMethodField()
    financial_history = FinancialSerializer(many=True, read_only=True)
    source_documents = SourceDocumentSerializer(many=True, read_only=True)
    news_mentions = NewsMentionSerializer(many=True, read_only=True)
    data_freshness = serializers.SerializerMethodField()

    class Meta(CharitySummarySerializer.Meta):
        fields = CharitySummarySerializer.Meta.fields + (
            "description",
            "founded_year",
            "donation_url",
            "money_breakdown",
            "financial_history",
            "source_documents",
            "news_mentions",
            "methodology_note",
            "ingestion_source",
            "data_freshness",
        )

    def get_money_breakdown(self, obj: Charity) -> dict[str, Any] | None:
        return _money_breakdown_from_financial(obj)

    def get_data_freshness(self, obj: Charity) -> dict[str, Any]:
        return {
            "last_synced_at": obj.updated_at.isoformat(),
            "source": obj.get_ingestion_source_display(),
        }


class CharityComparisonSerializer(CharitySummarySerializer):
    money_breakdown = serializers.SerializerMethodField()
    top_executive_comp_usd = serializers.SerializerMethodField()
    donation_url = serializers.URLField()
    primary_source_document = serializers.SerializerMethodField()

    class Meta(CharitySummarySerializer.Meta):
        fields = CharitySummarySerializer.Meta.fields + (
            "money_breakdown",
            "top_executive_comp_usd",
            "donation_url",
            "primary_source_document",
        )

    def get_money_breakdown(self, obj: Charity) -> dict[str, Any] | None:
        return _money_breakdown_from_financial(obj)

    def get_top_executive_comp_usd(self, obj: Charity) -> float | None:
        latest = obj.financial_history.order_by("-year").first()
        if latest is None or latest.top_executive_comp_usd is None:
            return None
        return float(latest.top_executive_comp_usd)

    def get_primary_source_document(self, obj: Charity) -> dict[str, Any] | None:
        doc = (
            obj.source_documents.filter(kind__startswith="irs_990")
            .order_by("-filed_date")
            .first()
            or obj.source_documents.order_by("-filed_date").first()
        )
        if doc is None:
            return None
        return SourceDocumentSerializer(doc).data
