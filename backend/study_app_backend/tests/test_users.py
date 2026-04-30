import pytest


ME_URL = '/api/v1/users/me/'


@pytest.mark.django_db
class TestGetMe:
    def test_child_profile(self, child_client, child_user):
        """TC-USER-001"""
        resp = child_client.get(ME_URL)
        assert resp.status_code == 200
        assert resp.data['role'] == 'child'
        assert 'nickname' in resp.data
        assert 'grade' in resp.data
        assert 'avatar' in resp.data

    def test_parent_profile(self, parent_client):
        """TC-USER-002"""
        resp = parent_client.get(ME_URL)
        assert resp.status_code == 200
        assert resp.data['role'] == 'parent'
        assert 'display_name' in resp.data

    def test_unauthenticated(self, api_client):
        """TC-USER-004"""
        resp = api_client.get(ME_URL)
        assert resp.status_code == 401


@pytest.mark.django_db
class TestPatchMe:
    def test_update_child_profile(self, child_client, child_user):
        """TC-USER-003"""
        resp = child_client.patch(ME_URL, {'nickname': 'kenta', 'grade': 4}, format='json')
        assert resp.status_code == 200
        assert resp.data['nickname'] == 'kenta'
        assert resp.data['grade'] == 4

        child_user.child_profile.refresh_from_db()
        assert child_user.child_profile.grade == 4

    def test_grade_out_of_range_low(self, child_client):
        """TC-USER-005: grade=0"""
        resp = child_client.patch(ME_URL, {'grade': 0}, format='json')
        assert resp.status_code == 400

    def test_grade_out_of_range_high(self, child_client):
        """TC-USER-005: grade=10"""
        resp = child_client.patch(ME_URL, {'grade': 10}, format='json')
        assert resp.status_code == 400
