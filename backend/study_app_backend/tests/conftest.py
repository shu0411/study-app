import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, ChildProfile, ParentProfile, ParentChildRelation
from apps.quiz.models import Subject, Unit, Topic, Question, Choice


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def child_user(db):
    user = User.objects.create_user(
        username='testchild',
        email='child@test.com',
        password='Pass1234',
        role=User.ROLE_CHILD,
    )
    ChildProfile.objects.create(user=user, nickname='テスト太郎', grade=3)
    return user


@pytest.fixture
def child_token(child_user):
    return str(RefreshToken.for_user(child_user).access_token)


@pytest.fixture
def child_client(api_client, child_token):
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {child_token}')
    return api_client


@pytest.fixture
def parent_user(db):
    user = User.objects.create_user(
        username='testparent',
        email='parent@test.com',
        password='Pass1234',
        role=User.ROLE_PARENT,
    )
    ParentProfile.objects.create(user=user, display_name='テスト親')
    return user


@pytest.fixture
def parent_token(parent_user):
    return str(RefreshToken.for_user(parent_user).access_token)


@pytest.fixture
def parent_client(api_client, parent_token):
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {parent_token}')
    return api_client


@pytest.fixture
def child_user2(db):
    user = User.objects.create_user(
        username='testchild2',
        email='child2@test.com',
        password='Pass1234',
        role=User.ROLE_CHILD,
    )
    ChildProfile.objects.create(user=user, nickname='テスト次郎', grade=4)
    return user


@pytest.fixture
def subject(db):
    return Subject.objects.create(name='算数', order=1)


@pytest.fixture
def unit(db, subject):
    return Unit.objects.create(subject=subject, name='計算', order=1)


@pytest.fixture
def topic(db, unit):
    return Topic.objects.create(unit=unit, name='足し算', order=1, target_grade=2)


@pytest.fixture
def question(db, topic):
    return Question.objects.create(
        topic=topic,
        body='1 + 1 = ?',
        question_type='single_choice',
        difficulty=1,
        order=1,
    )


@pytest.fixture
def correct_choice(db, question):
    return Choice.objects.create(question=question, body='2', is_correct=True, order=1)


@pytest.fixture
def wrong_choice(db, question):
    return Choice.objects.create(question=question, body='3', is_correct=False, order=2)


@pytest.fixture
def linked_relation(db, parent_user, child_user):
    return ParentChildRelation.objects.create(
        parent=parent_user.parent_profile,
        child=child_user.child_profile,
    )
