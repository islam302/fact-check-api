import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, MagicMock
from auth_app.models import CustomUser


import pytest

@pytest.fixture(autouse=True)
def disable_migrations(settings):
    settings.MIGRATION_MODULES = {
        "EmailTrack": None,
        "recipients": None,
    }

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    user = CustomUser.objects.create_user(
        username="admin", email="admin@test.com",
        role="admin", password="pass123"
    )
    return user


@pytest.fixture
def normal_user(db):
    user = CustomUser.objects.create_user(
        username="normal", email="normal@test.com",
        role="user", password="pass123"
    )
    return user


def auth_client(client, user):
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return client


# ========== CustomTokenObtainPairView ==========
def test_token_obtain_pair(api_client, normal_user):
    url = reverse("token_obtain_pair")
    res = api_client.post(url, {"username": "normal", "password": "pass123"})
    assert res.status_code == 200
    assert "access" in res.data
    assert res.data["username"] == "normal"


# ========== PasswordResetRequestView ==========
@patch("auth_app.views.send_reset_password_email", return_value=True)
def test_password_reset_request_success(mock_send, api_client, normal_user):
    url = reverse("password_reset")
    res = api_client.post(url, {"email": "normal@test.com"})
    assert res.status_code == 200
    assert "تم إرسال بريد" in res.data["message"]


def test_password_reset_request_not_found(api_client):
    url = reverse("password_reset")
    res = api_client.post(url, {"email": "notfound@test.com"})
    assert res.status_code == 404


def test_password_reset_request_no_email(api_client):
    url = reverse("password_reset")
    res = api_client.post(url, {})
    assert res.status_code == 400


# ========== PasswordResetConfirmAPIView ==========
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

def test_password_reset_confirm_success(api_client, normal_user):
    uidb64 = urlsafe_base64_encode(force_bytes(normal_user.pk))
    token = default_token_generator.make_token(normal_user)
    url = reverse("password_reset_confirm_api", args=[uidb64, token])
    res = api_client.post(url, {"password": "newpass"})
    assert res.status_code == 200
    normal_user.refresh_from_db()
    assert normal_user.check_password("newpass")


def test_password_reset_confirm_invalid_uid(api_client):
    url = reverse("password_reset_confirm_api", args=["bad", "token"])
    res = api_client.post(url, {"password": "whatever"})
    assert res.status_code == 400


# ========== UserStatusView ==========
def test_user_status_admin(api_client, admin_user):
    url = reverse("user-status")
    client = auth_client(api_client, admin_user)
    res = client.get(url)
    assert res.status_code == 200
    assert "email" in res.data
    assert res.data["role"] == "admin"


def test_user_status_normal(api_client, normal_user):
    url = reverse("user-status")
    client = auth_client(api_client, normal_user)
    res = client.get(url)
    assert res.status_code == 200
    assert "email" in res.data
    assert res.data["role"] == "user"
