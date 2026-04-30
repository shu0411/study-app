import uuid
import pytest

from apps.progress.models import AnswerHistory


ANSWERS_URL = '/api/v1/progress/answers/'
SUMMARY_URL = '/api/v1/progress/summary/'


def child_summary_url(child_id):
    return f'/api/v1/progress/children/{child_id}/summary/'


@pytest.mark.django_db
class TestAnswerSubmit:
    def test_correct_answer(self, child_client, question, correct_choice, wrong_choice):
        """TC-PROG-001"""
        resp = child_client.post(ANSWERS_URL, {
            'question_id': str(question.id),
            'selected_choice_id': str(correct_choice.id),
        }, format='json')
        assert resp.status_code == 201
        assert resp.data['is_correct'] is True
        assert AnswerHistory.objects.filter(is_correct=True).count() == 1

    def test_wrong_answer(self, child_client, question, correct_choice, wrong_choice):
        """TC-PROG-002"""
        resp = child_client.post(ANSWERS_URL, {
            'question_id': str(question.id),
            'selected_choice_id': str(wrong_choice.id),
        }, format='json')
        assert resp.status_code == 201
        assert resp.data['is_correct'] is False

    def test_reanswer_adds_record(self, child_client, question, correct_choice, wrong_choice):
        """TC-PROG-003: 再解答は追記（上書きではない）"""
        child_client.post(ANSWERS_URL, {
            'question_id': str(question.id),
            'selected_choice_id': str(correct_choice.id),
        }, format='json')
        child_client.post(ANSWERS_URL, {
            'question_id': str(question.id),
            'selected_choice_id': str(wrong_choice.id),
        }, format='json')
        assert AnswerHistory.objects.count() == 2

    def test_wrong_choice_for_question(self, child_client, topic, question, correct_choice):
        """TC-PROG-006: 別問題の選択肢を指定 → 400"""
        from apps.quiz.models import Question, Choice
        other_q = Question.objects.create(
            topic=topic, body='2 + 2 = ?', question_type='single_choice', difficulty=1, order=2,
        )
        other_choice = Choice.objects.create(
            question=other_q, body='4', is_correct=True, order=1,
        )
        resp = child_client.post(ANSWERS_URL, {
            'question_id': str(question.id),
            'selected_choice_id': str(other_choice.id),
        }, format='json')
        assert resp.status_code == 400

    def test_nonexistent_question(self, child_client, correct_choice):
        """TC-PROG-007"""
        resp = child_client.post(ANSWERS_URL, {
            'question_id': str(uuid.uuid4()),
            'selected_choice_id': str(correct_choice.id),
        }, format='json')
        assert resp.status_code == 404

    def test_parent_cannot_answer(self, parent_client, question, correct_choice):
        """TC-PROG-008"""
        resp = parent_client.post(ANSWERS_URL, {
            'question_id': str(question.id),
            'selected_choice_id': str(correct_choice.id),
        }, format='json')
        assert resp.status_code == 403


@pytest.mark.django_db
class TestProgressSummary:
    def test_child_own_summary(self, child_client, child_user, question, correct_choice, wrong_choice):
        """TC-PROG-004"""
        AnswerHistory.objects.create(
            child=child_user.child_profile,
            question=question,
            selected_choice=correct_choice,
            is_correct=True,
        )
        AnswerHistory.objects.create(
            child=child_user.child_profile,
            question=question,
            selected_choice=wrong_choice,
            is_correct=False,
        )
        resp = child_client.get(SUMMARY_URL)
        assert resp.status_code == 200
        assert len(resp.data) == 1
        row = resp.data[0]
        assert row['total'] == 2
        assert row['correct'] == 1
        assert abs(row['accuracy_rate'] - 0.5) < 0.001

    def test_parent_views_child_summary(self, parent_client, parent_user, child_user,
                                        linked_relation, question, correct_choice):
        """TC-PROG-005"""
        AnswerHistory.objects.create(
            child=child_user.child_profile,
            question=question,
            selected_choice=correct_choice,
            is_correct=True,
        )
        resp = parent_client.get(child_summary_url(child_user.id))
        assert resp.status_code == 200
        assert resp.data[0]['total'] == 1

    def test_child_cannot_view_others_summary(self, child_client, child_user2):
        """TC-PROG-009"""
        resp = child_client.get(child_summary_url(child_user2.id))
        assert resp.status_code == 403

    def test_parent_cannot_view_unlinked_child(self, parent_client, child_user):
        """TC-PROG-010: 紐付けなし → 404"""
        resp = parent_client.get(child_summary_url(child_user.id))
        assert resp.status_code == 404
