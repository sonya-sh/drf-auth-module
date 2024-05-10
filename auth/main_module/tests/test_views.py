import pytest
import os
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.exceptions import TokenError
from main_module.jwt_tokens.tokens import CustomRefreshToken, redis_client

os.environ["DJANGO_SETTINGS_MODULE"] = "auth.settings"

@pytest.fixture
def redis_client_fixture():
    yield
    redis_client.flushdb()

@pytest.fixture
def user():
    return get_user_model().objects.create(email=f"autotest_username@mail.ru", password="test_password")

@pytest.fixture
def refresh_token(user):
    token = CustomRefreshToken.for_user(user)
    return token

@pytest.fixture
def access_token(refresh_token):
    token = refresh_token.access_token
    return token

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_blacklist_token(refresh_token, redis_client_fixture):
    refresh_token.blacklist()

    assert redis_client.exists(refresh_token["jti"])
    exp_time = redis_client.ttl(refresh_token["jti"])
    assert exp_time == int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].seconds) - 1
    
    with pytest.raises(TokenError):
        refresh_token.check_blacklist()

    redis_client.flushdb()

@pytest.mark.django_db
def test_access_protected_resource(api_client, access_token):

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    response = api_client.get("/api/v1/userslist/")

    assert response.status_code == 200