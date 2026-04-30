from django.contrib import admin
from .models import AnswerHistory


@admin.register(AnswerHistory)
class AnswerHistoryAdmin(admin.ModelAdmin):
    list_display = ['child', 'question', 'is_correct', 'answered_at']
    list_filter = ['is_correct']
    readonly_fields = ['answered_at']
