from allauth.account import app_settings
from allauth.account.models import (
    EmailAddress,
    EmailConfirmation,
    EmailConfirmationHMAC,
)
from allauth.socialaccount.models import SocialAccount
from dj_rest_auth.jwt_auth import (
    CookieTokenRefreshSerializer,
    set_jwt_access_cookie,
    set_jwt_refresh_cookie,
)
from dj_rest_auth.registration.views import VerifyEmailView as DjRestVerifyEmailView
from dj_rest_auth.views import LoginView
from django.conf import settings
from django.contrib.auth import logout
from django.core.mail import EmailMultiAlternatives
from django.core.signing import BadSignature, Signer
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from users.api.v1.serializers import (
    ContactUsSerializer,
    ProfilePictureSerializer,
    UserDetailSerializer,
)
from users.constants import COOKIES_TO_DELETE, MAX_PROFILE_PIC_UPLOAD_SIZE
from users.models import User
from users.utils import generate_unique_username


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        responses={200: UserDetailSerializer(many=False)},
    )
    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=UserDetailSerializer,
        responses={200: UserDetailSerializer(many=False)},
    )
    def put(self, request):
        serializer = UserDetailSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=UserDetailSerializer,
        responses={200: UserDetailSerializer(many=False)},
    )
    def patch(self, request):
        serializer = UserDetailSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={200: "A confirmation email has been sent."})
    def delete(self, request):
        user = request.user
        signer = Signer()
        token = signer.sign(user.id)
        delete_account_url = f"{settings.FRONTEND_URL}/user/delete?token={token}"

        subject = "Confirm Account Deletion"
        context = {
            "user": user,
            "delete_account_url": delete_account_url,
        }
        email_template = "account/email/account_deletion_confirmation.html"
        html_content = render_to_string(email_template, context)
        email = EmailMultiAlternatives(
            subject, "", settings.DEFAULT_FROM_EMAIL, [user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        return Response(
            {"detail": "A confirmation email has been sent."}, status=status.HTTP_200_OK
        )


class ProfilePictureUploadView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        if len(request.FILES) == 0:
            return Response(
                {"error": "No file was uploaded."}, status=status.HTTP_400_BAD_REQUEST
            )
        if len(request.FILES) > 1:
            return Response(
                {"error": "Exactly one file must be uploaded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile_picture = request.FILES["profile_picture"]
        if profile_picture.size > MAX_PROFILE_PIC_UPLOAD_SIZE:
            return Response(
                {"error": "File size must be less than 5MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        serializer = ProfilePictureSerializer(instance=user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomLoginView(LoginView):
    def get_response(self):
        response = super().get_response()

        refresh = RefreshToken.for_user(self.user)
        response.data["refresh"] = str(refresh)

        return response


class CustomVerifyEmailView(DjRestVerifyEmailView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            key = serializer.validated_data["key"]

            confirmation = EmailConfirmationHMAC.from_key(key)
            if not confirmation:
                confirmation = EmailConfirmation.objects.get(key=key)

                expiration_date = confirmation.created + timezone.timedelta(
                    days=app_settings.EMAIL_CONFIRMATION_EXPIRE_DAYS
                )
                if expiration_date <= timezone.now():
                    return Response(
                        {"key": [_("Verification key has expired")]},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if confirmation.email_address.verified:
                return Response(
                    {"detail": _("Email already verified")}, status=status.HTTP_200_OK
                )

            confirmation.confirm(self.request)

            return Response(
                {
                    "detail": _("Email successfully verified"),
                    "email": confirmation.email_address.email,
                },
                status=status.HTTP_200_OK,
            )

        except (EmailConfirmation.DoesNotExist, ValueError):
            return Response(
                {"key": [_("Invalid verification key")]},
                status=status.HTTP_400_BAD_REQUEST,
            )


# override get_refresh_view to add refresh token in payload
def get_refresh_view():
    """Returns a Token Refresh CBV without a circular import"""
    from rest_framework_simplejwt.settings import api_settings as jwt_settings
    from rest_framework_simplejwt.views import TokenRefreshView

    class RefreshViewWithCookieSupport(TokenRefreshView):
        serializer_class = CookieTokenRefreshSerializer

        def finalize_response(self, request, response, *args, **kwargs):
            if response.status_code == status.HTTP_200_OK and "access" in response.data:
                set_jwt_access_cookie(response, response.data["access"])
                response.data["access_expiration"] = (
                    timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME
                )
            if (
                response.status_code == status.HTTP_200_OK
                and "refresh" in response.data
            ):
                set_jwt_refresh_cookie(response, response.data["refresh"])
                response.data["refresh_expiration"] = (
                    timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME
                )
            return super().finalize_response(request, response, *args, **kwargs)

    return RefreshViewWithCookieSupport


class ConfirmDeletionView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "token",
                openapi.IN_QUERY,
                description="Token for confirming account deletion",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ]
    )
    def post(self, request):
        token = request.query_params.get("token")

        try:
            signer = Signer()
            user_id = signer.unsign(token)
            user = User.objects.get(id=user_id)
            if user != request.user:
                return Response(
                    {"detail": "You do not have permission to delete this account."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Delete EmailAddress and SocialAccount instances of the user
            EmailAddress.objects.filter(user=user).delete()
            SocialAccount.objects.filter(user=user).delete()

            user.is_active = False
            user.username = generate_unique_username()
            user.email = f"deleted_{user.id}@deleted.com"
            user.first_name = "Deleted"
            user.last_name = "User"
            user.phone_number = None
            user.birthday = None
            user.profile_picture = None

            user.set_unusable_password()

            user.save()

            OutstandingToken.objects.filter(user=user).delete()

            logout(request)

            response = Response(
                {"detail": "User deleted successfully."}, status=status.HTTP_200_OK
            )

            for cookie in COOKIES_TO_DELETE:
                response.delete_cookie(cookie)

            return response

        except (User.DoesNotExist, BadSignature):
            return Response(
                {"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
            )


class ContactUsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(type=openapi.TYPE_STRING),
                "email": openapi.Schema(type=openapi.TYPE_STRING),
                "phone_number": openapi.Schema(type=openapi.TYPE_STRING),
                "message": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={201: "Contact Us submission received."},
    )
    def post(self, request):
        serializer = ContactUsSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            current_time = timezone.localtime(timezone.now())
            date_time_submitted = current_time.strftime("%B %d, %Y %I:%M %p")

            context = {
                "date_time_submitted": date_time_submitted,
                "name": data["name"],
                "email_address": data["email"],
                "phone_number": data["phone_number"],
                "message": data["message"],
                "user": {"is_authenticated": True},
            }
            email_template = "account/email/contact_us_submission.html"
            html_content = render_to_string(email_template, context)

            subject = "New Contact Us Submission"
            active_admins = User.objects.filter(is_active=True, is_staff=True)
            admin_emails = [admin.email for admin in active_admins]

            email = EmailMultiAlternatives(
                subject, "", settings.DEFAULT_FROM_EMAIL, admin_emails
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            return Response(
                {"detail": "Contact Us submission received."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
