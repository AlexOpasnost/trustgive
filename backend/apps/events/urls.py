from django.urls import path

from apps.events.views import DonationRedirectView

urlpatterns = [
    path(
        "events/donation-redirect/",
        DonationRedirectView.as_view(),
        name="donation-redirect",
    ),
]
