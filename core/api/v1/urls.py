from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.api.v1.viewsets import ConstanceViewSet, SocialAccountViewSet

router = DefaultRouter()
router.register(r"constance", ConstanceViewSet, basename="constance")
router.register(r"social-accounts", SocialAccountViewSet, basename="social-accounts")

urlpatterns = [
    path("", include(router.urls)),
]
