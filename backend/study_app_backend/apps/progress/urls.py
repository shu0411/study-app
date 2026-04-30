from django.urls import path

from .views import AnswerSubmitView, ProgressSummaryView, ChildProgressSummaryView

urlpatterns = [
    path('progress/answers/', AnswerSubmitView.as_view()),
    path('progress/summary/', ProgressSummaryView.as_view()),
    path('progress/children/<uuid:child_id>/summary/', ChildProgressSummaryView.as_view()),
]
