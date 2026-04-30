import uuid
import pytest

from apps.accounts.models import ParentChildRelation


CHILDREN_URL = '/api/v1/parents/me/children/'


def child_detail_url(child_id):
    return f'/api/v1/parents/me/children/{child_id}/'


@pytest.mark.django_db
class TestGetChildren:
    def test_list_linked_children(self, parent_client, parent_user, child_user, child_user2):
        """TC-PC-001: 2人紐付き済みの場合2件返る"""
        ParentChildRelation.objects.create(
            parent=parent_user.parent_profile,
            child=child_user.child_profile,
        )
        ParentChildRelation.objects.create(
            parent=parent_user.parent_profile,
            child=child_user2.child_profile,
        )
        resp = parent_client.get(CHILDREN_URL)
        assert resp.status_code == 200
        assert len(resp.data) == 2

    def test_child_cannot_access(self, child_client):
        """TC-PC-004"""
        resp = child_client.get(CHILDREN_URL)
        assert resp.status_code == 403


@pytest.mark.django_db
class TestLinkChild:
    def test_success(self, parent_client, child_user):
        """TC-PC-002"""
        resp = parent_client.post(CHILDREN_URL, {
            'child_id': str(child_user.id),
        }, format='json')
        assert resp.status_code == 201
        assert ParentChildRelation.objects.count() == 1

    def test_duplicate_link(self, parent_client, linked_relation, child_user):
        """TC-PC-005"""
        resp = parent_client.post(CHILDREN_URL, {
            'child_id': str(child_user.id),
        }, format='json')
        assert resp.status_code == 400

    def test_nonexistent_child_id(self, parent_client):
        """TC-PC-006"""
        resp = parent_client.post(CHILDREN_URL, {
            'child_id': str(uuid.uuid4()),
        }, format='json')
        assert resp.status_code == 404


@pytest.mark.django_db
class TestUnlinkChild:
    def test_success(self, parent_client, linked_relation, child_user):
        """TC-PC-003"""
        resp = parent_client.delete(child_detail_url(child_user.id))
        assert resp.status_code == 204
        assert ParentChildRelation.objects.count() == 0

    def test_other_parents_child(self, parent_client, child_user2):
        """TC-PC-007: 自分と無関係な子どもは 404"""
        resp = parent_client.delete(child_detail_url(child_user2.id))
        assert resp.status_code == 404
