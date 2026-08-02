"""Response shape for the "Is X legitimate?" landing payload.

These serializers are never used to parse input — the endpoint is read-only and
builds its response as a plain dict. They exist so that `manage.py spectacular`
can describe the endpoint instead of skipping it.

That skipping was not cosmetic. `SeoCharityView` is a bare `APIView`, so
drf-spectacular could not guess a response type and emitted
"unable to guess serializer … Ignoring view for now" — an *error*, which under
CI's `--fail-on-warn` aborted schema generation, which is the step that runs
before pytest. One undocumented view was therefore the reason no backend test
had run in CI. It also meant the published OpenAPI schema silently omitted the
endpoint the frontend generates its types from (`npm run gen-api`).

The field names and types below mirror `SeoCharityView.get` exactly; the two are
close enough to read side by side, and the contract test in
`tests/test_seo_schema.py` fails if they drift.
"""

from __future__ import annotations

from rest_framework import serializers

from apps.charities.serializers import CharityDetailSerializer
from apps.core.serializers import LocalizedSerializerField


class SeoMetaSerializer(serializers.Serializer):
    """`meta` — everything the page needs for its <head> and structured data."""

    title = serializers.CharField(
        help_text="Page title, already clamped to 70 characters.",
    )
    description = serializers.CharField(
        help_text="Meta description, already clamped to 160 characters.",
    )
    canonical_url = serializers.CharField(
        help_text="Language-scoped canonical path for this landing page.",
    )
    og_image_url = serializers.URLField(
        help_text="Open Graph preview image for the landing page.",
    )
    structured_data = serializers.DictField(
        help_text="schema.org NGO object, ready to embed as JSON-LD.",
    )


class SeoCharityPayloadSerializer(serializers.Serializer):
    """Full payload of `GET /api/seo/charities/{slug}/`."""

    slug = serializers.SlugField()
    h1 = serializers.CharField(
        help_text='The question the page answers, e.g. "Is GiveWell a legitimate charity?"',
    )
    answer = serializers.CharField(
        help_text='The verdict in the requested language, e.g. "Yes — verified."',
    )
    evidence_summary = LocalizedSerializerField(
        help_text=(
            "One sentence of evidence, in both languages, so a client-side "
            "language toggle needs no second request."
        ),
    )
    meta = SeoMetaSerializer()
    charity = CharityDetailSerializer(
        help_text="The full charity record, reused to render the proof list.",
    )
