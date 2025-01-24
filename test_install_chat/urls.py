
from allauth.account.views import ConfirmEmailView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from oauth2_provider import urls as oauth2_urls
from django.views.generic import TemplateView
from users.api.v1.views import CustomLoginView, ProfilePictureUploadView, UserDetailView, CustomVerifyEmailView, get_refresh_view, ConfirmDeletionView, ContactUsView
from core.api.v1.views import (
    DisconnectSocialAccountView,
    FacebookConnectView,
    FacebookLoginView,
    GoogleLoginView,
    GoogleConnectView,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/oauth2/", include(oauth2_urls, namespace="oauth2_provider")),
    path("accounts/", include("allauth.urls")),

    path(
        "password/reset/confirm/<uidb64>/<token>/",
        TemplateView.as_view(template_name="accounts/password_reset_confirm.html"),
        name="password_reset_confirm",
    ),

    # v1 APIs
    path(
        "api/v1/",
        include(
            (
                [
                    path("auth/confirm-deletion/", ConfirmDeletionView.as_view(), name="confirm_deletion"),
                    path("auth/contact-us/", ContactUsView.as_view(), name="contact_us"),
                    path('profile/picture/', ProfilePictureUploadView.as_view(), name='profile_picture_upload'),
                    path("auth/user/", UserDetailView.as_view(), name="user_detail"),
                    path("auth/login/", CustomLoginView.as_view(), name="rest_login"),
                    path(
                        "auth/token/refresh/",
                        get_refresh_view().as_view(),
                        name="token_refresh",
                    ),
                    path("auth/", include("dj_rest_auth.urls")),
                    path("auth/registration/verify-email/", 
                         CustomVerifyEmailView.as_view(), 
                         name="rest_verify_email"),
                    path("auth/registration/", include("dj_rest_auth.registration.urls")),
                    path(
                        "auth/social/facebook/login/",
                        FacebookLoginView.as_view(),
                        name="facebook_login",
                    ),
                    path(
                        "auth/social/facebook/connect/",
                        FacebookConnectView.as_view(),
                        name="facebook_login",
                    ),
                    path(
                        "auth/social/google/login/",
                        GoogleLoginView.as_view(),
                        name="google_login",
                    ),
                    path(
                        "auth/social/google/connect/",
                        GoogleConnectView.as_view(),
                        name="google_connect",
                    ),
                    path(
                        "auth/token/refresh/",
                        TokenRefreshView.as_view(),
                        name="token_refresh",
                    ),
                    path(
                        "auth/social/disconnect/",
                        DisconnectSocialAccountView.as_view(),
                        name="social_disconnect",
                    ),
                    path(
                        "core/",
                        include(
                            ("core.api.v1.urls", "core"),
                            namespace="core",
                        ),
                    ),
                ],
                "v1",
            ),
            namespace="v1",
        ),
    ),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Swagger
api_info = openapi.Info(
    title="test-install-chat API",
    default_version="v1",
    description="API documentation for test-install-chat",
)

schema_view = get_schema_view(
    api_info,
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=(JWTAuthentication,),
)


urlpatterns += [
    path("api/docs/", schema_view.with_ui("swagger", cache_timeout=0), name="api_docs"),
]


admin.site.site_header = "test-install-chat"
admin.site.site_title = "test-install-chat Admin Portal"
admin.site.index_title = "test-install-chat Admin"
