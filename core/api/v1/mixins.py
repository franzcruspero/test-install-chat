from rest_framework_simplejwt.tokens import RefreshToken


class TokenResponseMixin:
    def get_token_response(self, user):
        refresh = RefreshToken.for_user(user)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}
