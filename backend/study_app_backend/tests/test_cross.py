import uuid
import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestCrosscutting:
    def test_expired_access_token_returns_401(self, api_client):
        """TC-CROSS-001: 不正なトークン → 401"""
        api_client.credentials(HTTP_AUTHORIZATION='Bearer invalidaccesstoken')
        resp = api_client.get('/api/v1/users/me/')
        assert resp.status_code == 401

    def test_malformed_bearer_token(self, api_client):
        """TC-CROSS-002: 形式不正の Bearer → 401"""
        api_client.credentials(HTTP_AUTHORIZATION='Bearer')
        resp = api_client.get('/api/v1/users/me/')
        assert resp.status_code == 401

    def test_non_uuid_path_param_returns_404(self, child_client):
        """TC-CROSS-003: UUID でないパスパラメータ → 404"""
        resp = child_client.get('/api/v1/quiz/subjects/not-a-uuid/units/')
        assert resp.status_code == 404

    def test_cors_preflight_allowed_origin(self, api_client):
        """TC-CROSS-004: 許可オリジンへの CORS プリフライト → 200"""
        resp = api_client.options(
            '/api/v1/auth/login/',
            HTTP_ORIGIN='http://localhost:5173',
            HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST',
        )
        assert resp.status_code == 200
        assert 'Access-Control-Allow-Origin' in resp
