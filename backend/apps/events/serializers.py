from rest_framework import serializers

from apps.events.models import DonationRedirectEvent, SourcePage


class DonationRedirectEventSerializer(serializers.ModelSerializer):
    source_page = serializers.ChoiceField(choices=SourcePage.choices, required=False, allow_blank=True)

    class Meta:
        model = DonationRedirectEvent
        fields = ("client_event_id", "charity_slug", "lang", "source_page")
