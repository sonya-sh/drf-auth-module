from typing import Any, Dict
import redis

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.tokens import AccessToken, Token, BlacklistMixin
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import AuthUser
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.utils import datetime_from_epoch, get_md5_hash_password

from datetime import datetime, timedelta

redis_client = redis.StrictRedis(host=settings.REDIS_HOST,
                                  port=settings.REDIS_PORT, db=settings.REDIS_DB)


class CustomBlacklistMixin(BlacklistMixin):
        
        payload: Dict[str, Any]

        if settings.BLACKLIST_USE:

            def verify(self, *args, **kwargs) -> None:
                self.check_blacklist()

                super().verify(*args, **kwargs)

            def check_blacklist(self) -> None:

                jti = self.payload["jti"]

                if redis_client.exists(jti):
                    raise TokenError(_("Token is blacklisted"))

            def blacklist(self) -> None:
                
                jti = self.payload[api_settings.JTI_CLAIM]
                exp = self.payload["exp"]
            
                token_str = str(self)
                exp_seconds = (datetime_from_epoch(exp) - timezone.now()).total_seconds()  # Вычисляем время жизни токена в секундах
                redis_client.setex(jti, int(exp_seconds), token_str)

            # @classmethod
            # def for_user(cls, user: AuthUser) -> "Token":

            #     user_id = getattr(user, api_settings.USER_ID_FIELD)
            #     if not isinstance(user_id, int):
            #         user_id = str(user_id)

            #     token = cls()
            #     token[api_settings.USER_ID_CLAIM] = user_id

            #     if api_settings.CHECK_REVOKE_TOKEN:
            #         token[api_settings.REVOKE_TOKEN_CLAIM] = get_md5_hash_password(
            #             user.password
            #     )

            #     return token


class AccessToken(Token):
    token_type = "access"
    lifetime = api_settings.ACCESS_TOKEN_LIFETIME


import uuid
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

