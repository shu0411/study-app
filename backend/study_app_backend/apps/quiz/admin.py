from django.contrib import admin
from .models import Subject, Unit, Topic, Question, Choice


class UnitInline(admin.TabularInline):
    model = Unit
    extra = 1


class TopicInline(admin.TabularInline):
    model = Topic
    extra = 1


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    inlines = [UnitInline]


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'order']
    list_filter = ['subject']
    inlines = [TopicInline]


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit', 'target_grade', 'order']
    list_filter = ['unit__subject', 'target_grade']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['body', 'topic', 'difficulty', 'question_type', 'order']
    list_filter = ['difficulty', 'topic__unit__subject']
    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['body', 'question', 'is_correct', 'order']
    list_filter = ['is_correct']
