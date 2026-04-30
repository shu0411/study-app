import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Subject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'subjects'
        ordering = ['order']

    def __str__(self):
        return self.name


class Unit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='units')
    name = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'units'
        ordering = ['order']

    def __str__(self):
        return f'{self.subject.name} > {self.name}'


class Topic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField(default=0)
    target_grade = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9)]
    )

    class Meta:
        db_table = 'topics'
        ordering = ['order']

    def __str__(self):
        return f'{self.unit} > {self.name}'


class Question(models.Model):
    TYPE_SINGLE_CHOICE = 'single_choice'
    TYPE_CHOICES = [(TYPE_SINGLE_CHOICE, '単一選択')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    body = models.TextField()
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_SINGLE_CHOICE)
    difficulty = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)]
    )
    explanation = models.TextField(blank=True, default='')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'questions'
        ordering = ['order']

    def __str__(self):
        return f'{self.topic.name}: {self.body[:30]}'


class Choice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    body = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'choices'
        ordering = ['order']

    def __str__(self):
        mark = '○' if self.is_correct else '×'
        return f'{mark} {self.body}'
