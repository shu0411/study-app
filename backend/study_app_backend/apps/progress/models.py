import uuid
from django.db import models
from apps.accounts.models import ChildProfile
from apps.quiz.models import Question, Choice


class AnswerHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, related_name='answer_histories')
    question = models.ForeignKey(Question, on_delete=models.PROTECT, related_name='answer_histories')
    selected_choice = models.ForeignKey(Choice, on_delete=models.PROTECT, related_name='answer_histories')
    is_correct = models.BooleanField()
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'answer_histories'
        indexes = [
            models.Index(fields=['child', 'question', 'answered_at']),
        ]

    def __str__(self):
        result = '正解' if self.is_correct else '不正解'
        return f'{self.child.nickname}: {self.question} → {result}'
