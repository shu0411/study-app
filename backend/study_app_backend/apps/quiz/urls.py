from django.urls import path

from .views import (
    SubjectListView,
    UnitListView,
    TopicListView,
    QuestionListView,
    QuestionDetailView,
)

urlpatterns = [
    path('quiz/subjects/', SubjectListView.as_view()),
    path('quiz/subjects/<uuid:subject_id>/units/', UnitListView.as_view()),
    path('quiz/units/<uuid:unit_id>/topics/', TopicListView.as_view()),
    path('quiz/topics/<uuid:topic_id>/questions/', QuestionListView.as_view()),
    path('quiz/questions/<uuid:id>/', QuestionDetailView.as_view()),
]
