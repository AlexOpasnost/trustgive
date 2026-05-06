from django.urls import path

from apps.core.views import DebugGiveDirectlyRawView, HealthView

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path(
        "_debug/givedirectly-raw/",
        DebugGiveDirectlyRawView.as_view(),
        name="debug-givedirectly-raw",
    ),
]
