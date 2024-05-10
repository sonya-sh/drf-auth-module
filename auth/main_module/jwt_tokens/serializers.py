from rest_framework import serializers
from main_module.jwt_tokens.tokens import CustomRefreshToken
from rest_framework_simplejwt.settings import api_settings
from typing import Any, Dict
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
#from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        token['permissions'] = [str(permission) for permission in user.user_permissions.all()]

        return token

class CustomTokenBlacklistSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True)
    token_class = CustomRefreshToken

    def validate(self, attrs: Dict[str, Any]) -> Dict[Any, Any]:
        refresh = self.token_class(attrs["refresh"])
        try:
            refresh.blacklist()
        except AttributeError:
            pass
        return {}
    
class CustomTokenRefreshSerializer(serializers.Serializer):
    
    refresh = serializers.CharField()
    access = serializers.CharField(read_only=True)
    token_class = CustomRefreshToken

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        # новый объект токена обновления на основе значения, содержащегося в атрибуте "refresh" словаря attrs.
        refresh = self.token_class(attrs["refresh"])

        data = {"access": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data["refresh"] = str(refresh)

        return data
