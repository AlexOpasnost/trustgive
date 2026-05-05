from django.urls import path

from apps.seo.views import SeoCharityView

urlpatterns = [
    path("seo/charities/<slug:slug>/", SeoCharityView.as_view(), name="seo-charity"),
]
