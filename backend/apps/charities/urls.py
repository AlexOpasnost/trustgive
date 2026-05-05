from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.charities.views import CauseListView, CharityViewSet, NewCharitiesFeed

router = DefaultRouter(trailing_slash=True)
router.register("charities", CharityViewSet, basename="charity")
router.register("causes", CauseListView, basename="cause")

urlpatterns = [
    path("", include(router.urls)),
    path("feed.rss", NewCharitiesFeed(), name="rss-feed"),
]
