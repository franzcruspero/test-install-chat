
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialConnectView, SocialLoginView
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from django.core.exceptions import ObjectDoesNotExist

from core.api.v1.serializers import DisconnectSocialAccountSerializer
from core.api.v1.mixins import TokenResponseMixin


class FacebookLoginView(SocialLoginView, TokenResponseMixin):
    permission_classes = [AllowAny]
    adapter_class = FacebookOAuth2Adapter
    client_class = OAuth2Client

    def get_response(self):
        response = super().get_response()
        token_response = self.get_token_response(self.user)
        response.data.update(token_response)
        return response


class GoogleLoginView(SocialLoginView, TokenResponseMixin):
    permission_classes = [AllowAny]
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client

    def get_response(self):
        response = super().get_response()
        token_response = self.get_token_response(self.user)
        response.data.update(token_response)
        return response


class FacebookConnectView(SocialConnectView, TokenResponseMixin):
    permission_classes = [IsAuthenticated]
    adapter_class = FacebookOAuth2Adapter
    client_class = OAuth2Client

    def get_response(self):
        response = super().get_response()
        token_response = self.get_token_response(self.user)
        response.data.update(token_response)
        return response


class GoogleConnectView(SocialConnectView, TokenResponseMixin):
    permission_classes = [IsAuthenticated]
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client

    def get_response(self):
        response = super().get_response()
        token_response = self.get_token_response(self.user)
        response.data.update(token_response)
        return response


class DisconnectSocialAccountView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DisconnectSocialAccountSerializer

    def post(self, request, *args, **kwargs):
        provider = request.data.get("provider")
        if provider:
            try:
                account = request.user.socialaccount_set.get(provider=provider)
                account.delete()
                return Response(
                    {"message": "Social account disconnected"},
                    status=status.HTTP_200_OK,
                )
            except ObjectDoesNotExist:
                return Response(
                    {"error": "Social account not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            {"error": "Provider not provided"}, status=status.HTTP_400_BAD_REQUEST
        )