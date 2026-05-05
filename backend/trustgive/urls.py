"""Root URL configuration for TrustGive."""
from django.contrib import admin
from django.http import HttpResponsePermanentRedirect
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def root_redirect(_request):
    return HttpResponsePermanentRedirect("/api/docs/")


urlpatterns = [
    path("", root_redirect),
    path("admin/", admin.site.urls),

    # API docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    # App URLs
    path("api/", include("apps.core.urls")),
    path("api/", include("apps.charities.urls")),
    path("api/", include("apps.events.urls")),
    path("api/", include("apps.seo.urls")),
]
