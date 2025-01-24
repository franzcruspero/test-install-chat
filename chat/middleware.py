import logging

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

from django.contrib.auth import get_user_model


logger = logging.getLogger(__name__)


@database_sync_to_async
def get_user_from_token(token):
    from rest_framework_simplejwt.exceptions import TokenError
    from rest_framework_simplejwt.tokens import AccessToken

    from django.contrib.auth.models import AnonymousUser

    User = get_user_model()

    try:
        access_token = AccessToken(token)
        return User.objects.get(id=access_token["user_id"])
    except TokenError as e:
        logger.error(f"Invalid token: {e}")
        return AnonymousUser()
    except User.DoesNotExist as e:
        logger.error(f"User not found: {e}")
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        from django.contrib.auth.models import AnonymousUser

        # Extract token from WebSocket headers
        headers = dict(scope.get("headers"))
        token = None
        for key, value in headers.items():
            if key == b"authorization":
                token = value.decode().split(" ")[1]  # Extract token after "Bearer"

        if token:
            scope["user"] = await get_user_from_token(token)
        else:
            scope["user"] = AnonymousUser()

        # If the user is anonymous and no token was provided, close the WebSocket connection
        if scope["user"].is_anonymous:
            await send(
                {
                    "type": "websocket.close",
                    "code": 4000,  # Code for abnormal closure
                }
            )
            return

        return await super().__call__(scope, receive, send)
