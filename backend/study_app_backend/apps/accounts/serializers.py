from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from .models import (
    User, ChildProfile, ParentProfile, ParentChildRelation,
    validate_username_format, validate_password_strength,
)


class ChildRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30, validators=[validate_username_format])
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password_strength])
    nickname = serializers.CharField(max_length=50)
    grade = serializers.IntegerField(min_value=1, max_value=9)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('このユーザーネームは既に使用されています。')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('このメールアドレスは既に使用されています。')
        return value

    @transaction.atomic
    def create(self, validated_data):
        nickname = validated_data.pop('nickname')
        grade = validated_data.pop('grade')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=User.ROLE_CHILD,
        )
        ChildProfile.objects.create(user=user, nickname=nickname, grade=grade)
        return user


class ParentRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30, validators=[validate_username_format])
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password_strength])
    display_name = serializers.CharField(max_length=100)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('このユーザーネームは既に使用されています。')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('このメールアドレスは既に使用されています。')
        return value

    @transaction.atomic
    def create(self, validated_data):
        display_name = validated_data.pop('display_name')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=User.ROLE_PARENT,
        )
        ParentProfile.objects.create(user=user, display_name=display_name)
        return user


class ChildProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)

    class Meta:
        model = ChildProfile
        fields = ['id', 'username', 'email', 'role', 'nickname', 'grade', 'avatar']

    def validate_grade(self, value):
        if not 1 <= value <= 9:
            raise serializers.ValidationError('学年は1〜9の範囲で入力してください。')
        return value


class ParentProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)

    class Meta:
        model = ParentProfile
        fields = ['id', 'username', 'email', 'role', 'display_name']


class ChildSummarySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='user.id', read_only=True)

    class Meta:
        model = ChildProfile
        fields = ['id', 'nickname', 'grade', 'avatar']


class ParentChildRelationCreateSerializer(serializers.Serializer):
    child_id = serializers.UUIDField()

    def validate_child_id(self, value):
        if not User.objects.filter(id=value, role=User.ROLE_CHILD).exists():
            raise NotFound('対象の子どもが見つかりません。')
        return value

    def create(self, validated_data):
        parent_profile = self.context['request'].user.parent_profile
        child_profile = User.objects.get(
            id=validated_data['child_id'], role=User.ROLE_CHILD
        ).child_profile
        relation, created = ParentChildRelation.objects.get_or_create(
            parent=parent_profile,
            child=child_profile,
        )
        if not created:
            raise serializers.ValidationError({'child_id': '既に紐付けされています。'})
        return relation
