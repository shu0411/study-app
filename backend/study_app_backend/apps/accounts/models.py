import uuid
import re
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


def validate_username_format(value):
    if not re.match(r'^[a-zA-Z0-9_]{3,30}$', value):
        raise ValidationError('ユーザーネームは3〜30文字の英数字・アンダースコアのみ使用できます。')


def validate_password_strength(value):
    if len(value) < 8:
        raise ValidationError('パスワードは8文字以上で入力してください。')
    if not re.search(r'[A-Za-z]', value):
        raise ValidationError('パスワードには英字を含めてください。')
    if not re.search(r'\d', value):
        raise ValidationError('パスワードには数字を含めてください。')


class User(AbstractUser):
    ROLE_CHILD = 'child'
    ROLE_PARENT = 'parent'
    ROLE_CHOICES = [(ROLE_CHILD, '子ども'), (ROLE_PARENT, '保護者')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[validate_username_format],
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['email', 'role']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f'{self.username} ({self.role})'


class ChildProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='child_profile')
    nickname = models.CharField(max_length=50)
    grade = models.PositiveSmallIntegerField()
    avatar = models.CharField(max_length=50, default='default')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'child_profiles'

    def __str__(self):
        return f'{self.nickname} (小{self.grade})'


class ParentProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    display_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'parent_profiles'

    def __str__(self):
        return self.display_name


class ParentChildRelation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(ParentProfile, on_delete=models.CASCADE, related_name='child_relations')
    child = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, related_name='parent_relations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'parent_child_relations'
        unique_together = [('parent', 'child')]

    def __str__(self):
        return f'{self.parent} → {self.child}'
