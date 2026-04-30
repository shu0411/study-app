import uuid
import pytest


@pytest.mark.django_db
class TestSubjectList:
    url = '/api/v1/quiz/subjects/'

    def test_success(self, child_client, subject):
        """TC-QUIZ-001"""
        resp = child_client.get(self.url)
        assert resp.status_code == 200
        assert len(resp.data) == 1
        assert resp.data[0]['name'] == subject.name
        assert 'id' in resp.data[0]
        assert 'order' in resp.data[0]

    def test_unauthenticated(self, api_client):
        """TC-QUIZ-007"""
        resp = api_client.get(self.url)
        assert resp.status_code == 401


@pytest.mark.django_db
class TestUnitList:
    def test_success(self, child_client, subject, unit):
        """TC-QUIZ-002"""
        resp = child_client.get(f'/api/v1/quiz/subjects/{subject.id}/units/')
        assert resp.status_code == 200
        assert len(resp.data) == 1
        assert resp.data[0]['name'] == unit.name

    def test_nonexistent_subject(self, child_client):
        """TC-QUIZ-006"""
        resp = child_client.get(f'/api/v1/quiz/subjects/{uuid.uuid4()}/units/')
        assert resp.status_code == 404


@pytest.mark.django_db
class TestTopicList:
    def test_success(self, child_client, unit, topic):
        """TC-QUIZ-003"""
        resp = child_client.get(f'/api/v1/quiz/units/{unit.id}/topics/')
        assert resp.status_code == 200
        assert len(resp.data) == 1
        assert 'target_grade' in resp.data[0]


@pytest.mark.django_db
class TestQuestionList:
    def test_success(self, child_client, topic, question):
        """TC-QUIZ-004: 選択肢は含まない"""
        resp = child_client.get(f'/api/v1/quiz/topics/{topic.id}/questions/')
        assert resp.status_code == 200
        assert len(resp.data) == 1
        data = resp.data[0]
        assert 'body' in data
        assert 'difficulty' in data
        assert 'choices' not in data


@pytest.mark.django_db
class TestQuestionDetail:
    def test_success_with_choices_no_is_correct(self, child_client, question, correct_choice, wrong_choice):
        """TC-QUIZ-005: choices を返すが is_correct は含まない"""
        resp = child_client.get(f'/api/v1/quiz/questions/{question.id}/')
        assert resp.status_code == 200
        assert 'choices' in resp.data
        assert len(resp.data['choices']) == 2
        for choice in resp.data['choices']:
            assert 'is_correct' not in choice

    def test_nonexistent(self, child_client):
        resp = child_client.get(f'/api/v1/quiz/questions/{uuid.uuid4()}/')
        assert resp.status_code == 404
