import pytest
from rest_framework_simplejwt.tokens import RefreshToken


REGISTER_CHILD_URL = '/api/v1/auth/register/child/'
REGISTER_PARENT_URL = '/api/v1/auth/register/parent/'
LOGIN_URL = '/api/v1/auth/login/'
REFRESH_URL = '/api/v1/auth/token/refresh/'
LOGOUT_URL = '/api/v1/auth/logout/'


@pytest.mark.django_db
class TestChildRegister:
    def test_success(self, api_client):
        """TC-AUTH-001"""
        resp = api_client.post(REGISTER_CHILD_URL, {
            'username': 'taro123',
            'email': 'taro@example.com',
            'password': 'Pass1234',
            'nickname': 'taro',
            'grade': 3,
        }, format='json')
        assert resp.status_code == 201
        assert resp.data['role'] == 'child'
        assert 'id' in resp.data

    def test_duplicate_username(self, api_client, child_user):
        """TC-AUTH-006"""
        resp = api_client.post(REGISTER_CHILD_URL, {
            'username': child_user.username,
            'email': 'other@example.com',
            'password': 'Pass1234',
            'nickname': 'x',
            'grade': 1,
        }, format='json')
        assert resp.status_code == 400
        assert 'username' in resp.data

    def test_invalid_password(self, api_client):
        """TC-AUTH-007: 短すぎ・数字なし"""
        resp = api_client.post(REGISTER_CHILD_URL, {
            'username': 'newuser1',
            'email': 'new@example.com',
            'password': 'abc',
            'nickname': 'x',
            'grade': 1,
        }, format='json')
        assert resp.status_code == 400

    def test_password_no_digit(self, api_client):
        """TC-AUTH-007: 英字のみ"""
        resp = api_client.post(REGISTER_CHILD_URL, {
            'username': 'newuser2',
            'email': 'new2@example.com',
            'password': 'Abcdefgh',
            'nickname': 'x',
            'grade': 1,
        }, format='json')
        assert resp.status_code == 400

    def test_password_no_letter(self, api_client):
        """TC-AUTH-007: 数字のみ"""
        resp = api_client.post(REGISTER_CHILD_URL, {
            'username': 'newuser3',
            'email': 'new3@example.com',
            'password': '12345678',
            'nickname': 'x',
            'grade': 1,
        }, format='json')
        assert resp.status_code == 400

    def test_username_too_short(self, api_client):
        """TC-AUTH-010: 2文字以下"""
        resp = api_client.post(REGISTER_CHILD_URL, {
            'username': 'ab',
            'email': 'x@example.com',
            'password': 'Pass1234',
            'nickname': 'x',
            'grade': 1,
        }, format='json')
        assert resp.status_code == 400

    def test_username_too_long(self, api_client):
        """TC-AUTH-010: 31文字以上"""
        resp = api_client.post(REGISTER_CHILD_URL, {
            'username': 'a' * 31,
            'email': 'x@example.com',
            'password': 'Pass1234',
            'nickname': 'x',
            'grade': 1,
        }, format='json')
        assert resp.status_code == 400

    def test_username_invalid_chars(self, api_client):
        """TC-AUTH-010: 記号含む"""
        resp = api_client.post(REGISTER_CHILD_URL, {
            'username': 'ta ro!',
            'email': 'x@example.com',
            'password': 'Pass1234',
            'nickname': 'x',
            'grade': 1,
        }, format='json')
        assert resp.status_code == 400


@pytest.mark.django_db
class TestParentRegister:
    def test_success(self, api_client):
        """TC-AUTH-002"""
        resp = api_client.post(REGISTER_PARENT_URL, {
            'username': 'parent01',
            'email': 'parent@example.com',
            'password': 'Pass1234',
            'display_name': 'Test Parent',
        }, format='json')
        assert resp.status_code == 201
        assert resp.data['role'] == 'parent'
        assert 'id' in resp.data


@pytest.mark.django_db
class TestLogin:
    def test_success(self, api_client, child_user):
        """TC-AUTH-003"""
        resp = api_client.post(LOGIN_URL, {
            'username': child_user.username,
            'password': 'Pass1234',
        }, format='json')
        assert resp.status_code == 200
        assert 'access' in resp.data
        assert 'refresh' in resp.data
        assert resp.data.get('role') == 'child'

    def test_wrong_password(self, api_client, child_user):
        """TC-AUTH-008"""
        resp = api_client.post(LOGIN_URL, {
            'username': child_user.username,
            'password': 'WrongPass1',
        }, format='json')
        assert resp.status_code == 401


@pytest.mark.django_db
class TestTokenRefresh:
    def test_success_and_rotation(self, api_client, child_user):
        """TC-AUTH-004: 更新成功 & 古いトークンが無効化される"""
        refresh = RefreshToken.for_user(child_user)
        old_refresh_str = str(refresh)

        resp = api_client.post(REFRESH_URL, {'refresh': old_refresh_str}, format='json')
        assert resp.status_code == 200
        assert 'access' in resp.data

        # 古い refresh は無効化されている
        resp2 = api_client.post(REFRESH_URL, {'refresh': old_refresh_str}, format='json')
        assert resp2.status_code == 401

    def test_invalid_token(self, api_client):
        """TC-AUTH-009"""
        resp = api_client.post(REFRESH_URL, {'refresh': 'invalidtoken'}, format='json')
        assert resp.status_code == 401


@pytest.mark.django_db
class TestLogout:
    def test_success(self, child_client, child_user):
        """TC-AUTH-005: ログアウト後に refresh が無効化される"""
        refresh = RefreshToken.for_user(child_user)
        refresh_str = str(refresh)

        resp = child_client.post(LOGOUT_URL, {'refresh': refresh_str}, format='json')
        assert resp.status_code == 204

        # ブラックリスト済みトークンで更新 → 401
        anon = APIClient()
        resp2 = anon.post(REFRESH_URL, {'refresh': refresh_str}, format='json')
        assert resp2.status_code == 401


# ローカルimportを避けるため上部でも import しておく
from rest_framework.test import APIClient  # noqa: E402
