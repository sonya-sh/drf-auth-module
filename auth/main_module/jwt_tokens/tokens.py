import redis

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.tokens import AccessToken, Token, BlacklistMixin
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import AuthUser
from rest_framework_simplejwt.settings import api_settings


redis_client = redis.StrictRedis(host=settings.REDIS_HOST,
                                  port=settings.REDIS_PORT, db=0)


class CustomBlacklistMixin(BlacklistMixin):

        def check_blacklist(self) -> None:

            jti = self.payload["jti"]

            if redis_client.exists(jti):
                raise TokenError(_("Token is blacklisted"))

        def blacklist(self) -> None:
            jti = self.payload[api_settings.JTI_CLAIM]
            exp = self.payload["exp"]
        
            token_str = str(self)
            redis_client.setex(jti, exp, token_str)

        @classmethod
        def for_user(cls, user: AuthUser) -> Token:

            token = super().for_user(user)  # type: ignore

            jti = token["jti"]
            exp = token["exp"]

            redis_client.setex(jti, exp - timezone.now, str(token))


            return token


class AccessToken(Token):
    token_type = "access"
    lifetime = api_settings.ACCESS_TOKEN_LIFETIME


class CustomRefreshToken(CustomBlacklistMixin, Token):
    token_type = "refresh"
    lifetime = api_settings.REFRESH_TOKEN_LIFETIME
    no_copy_claims = (
        api_settings.TOKEN_TYPE_CLAIM,
        "exp",
        api_settings.JTI_CLAIM,
        "jti",
    )
    access_token_class = AccessToken

    @property
    def access_token(self) -> AccessToken:

        access = self.access_token_class()
        access.set_exp(from_time=self.current_time)

        no_copy = self.no_copy_claims
        for claim, value in self.payload.items():
            if claim in no_copy:
                continue
            access[claim] = value

        return access

