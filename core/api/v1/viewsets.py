from allauth.socialaccount.models import SocialAccount
from constance import config
from constance import settings as constance_settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


from django.conf import settings

from core.api.v1.serializers import ConstanceSerializer, SocialAccountSerializer


class ConstanceViewSet(ViewSet):
    permission_classes = [AllowAny]
    def list(self, request):
        keys = [
            key
            for key in constance_settings.CONFIG.keys()
            if key not in settings.EXCLUDED_KEYS_FOR_API
        ]
        constance_values = [(key, getattr(config, key)) for key in keys]
        serializer = ConstanceSerializer(constance_values, many=True)
        return Response(serializer.data, status.HTTP_200_OK)


class SocialAccountViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        social_accounts = SocialAccount.objects.filter(user=user)
        providers = [account.provider for account in social_accounts]
        serializer = SocialAccountSerializer(providers)
        return Response([serializer.data], status=status.HTTP_200_OK)
