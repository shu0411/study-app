from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated

from .models import Subject, Unit, Topic, Question
from .serializers import (
    SubjectSerializer,
    UnitSerializer,
    TopicSerializer,
    QuestionListSerializer,
    QuestionDetailSerializer,
)


class SubjectListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all()


class UnitListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UnitSerializer

    def get_queryset(self):
        subject = get_object_or_404(Subject, id=self.kwargs['subject_id'])
        return subject.units.all()


class TopicListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TopicSerializer

    def get_queryset(self):
        unit = get_object_or_404(Unit, id=self.kwargs['unit_id'])
        return unit.topics.all()


class QuestionListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionListSerializer

    def get_queryset(self):
        topic = get_object_or_404(Topic, id=self.kwargs['topic_id'])
        return topic.questions.all()


class QuestionDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionDetailSerializer
    queryset = Question.objects.prefetch_related('choices')
    lookup_field = 'id'
