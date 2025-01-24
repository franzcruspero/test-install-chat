from rest_framework.routers import DefaultRouter
from rest_framework_extensions.routers import ExtendedDefaultRouter as DefaultRouter

from django.urls import include, path

from chat.api.v1.viewsets import ChatRoomViewSet, MessageViewSet


app_name = "chat"


router = DefaultRouter()
room_router = router.register("rooms", ChatRoomViewSet, basename="rooms")

# Nest Message routes into ChatRoom routes
room_router.register(
    "messages", MessageViewSet, basename="messages", parents_query_lookups=["room"]
)

urlpatterns = [
    path("", include(router.urls)),
]
