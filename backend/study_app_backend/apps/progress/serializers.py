from rest_framework import serializers
from rest_framework.exceptions import NotFound
from apps.quiz.models import Question, Choice
from .models import AnswerHistory


class AnswerSubmitSerializer(serializers.Serializer):
    question_id = serializers.UUIDField()
    selected_choice_id = serializers.UUIDField()

    def validate(self, attrs):
        try:
            question = Question.objects.get(id=attrs['question_id'])
        except Question.DoesNotExist:
            raise NotFound('問題が見つかりません。')

        try:
            choice = Choice.objects.get(id=attrs['selected_choice_id'], question=question)
        except Choice.DoesNotExist:
            raise serializers.ValidationError(
                {'selected_choice_id': 'この選択肢は指定された問題に属していません。'}
            )

        attrs['question'] = question
        attrs['choice'] = choice
        return attrs

    def create(self, validated_data):
        child_profile = self.context['request'].user.child_profile
        question = validated_data['question']
        choice = validated_data['choice']
        return AnswerHistory.objects.create(
            child=child_profile,
            question=question,
            selected_choice=choice,
            is_correct=choice.is_correct,
        )


class AnswerHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerHistory
        fields = ['id', 'question', 'selected_choice', 'is_correct', 'answered_at']


class SubjectSummarySerializer(serializers.Serializer):
    subject_id = serializers.UUIDField()
    subject_name = serializers.CharField()
    total = serializers.IntegerField()
    correct = serializers.IntegerField()
    accuracy_rate = serializers.FloatField()
