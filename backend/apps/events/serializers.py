from rest_framework import serializers

from apps.events.models import DonationRedirectEvent, SourcePage


class DonationRedirectEventSerializer(serializers.ModelSerializer):
    # client_event_id is the model's unique key; the view dedupes via
    # get_or_create, so the serializer must NOT auto-reject duplicates with
    # 400. Default ModelSerializer attaches a UniqueValidator that fires
    # before the view sees the request, breaking idempotency. Explicit empty
    # validators=[] disables it; uniqueness is still enforced at the DB layer
    # (and converted to 200/202 by get_or_create's no-op path).
    client_event_id = serializers.UUIDField(validators=[])
    source_page = serializers.ChoiceField(choices=SourcePage.choices, required=False, allow_blank=True)

    class Meta:
        model = DonationRedirectEvent
        fields = ("client_event_id", "charity_slug", "lang", "source_page")
