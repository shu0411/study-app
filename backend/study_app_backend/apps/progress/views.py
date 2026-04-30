from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import ChildProfile, ParentChildRelation
from apps.accounts.permissions import IsChild, IsParent
from .models import AnswerHistory
from .serializers import AnswerSubmitSerializer, SubjectSummarySerializer


def _build_summary(child_profile):
    rows = (
        AnswerHistory.objects.filter(child=child_profile)
        .values(
            subject_id=F('question__topic__unit__subject__id'),
            subject_name=F('question__topic__unit__subject__name'),
        )
        .annotate(
            total=Count('id'),
            correct=Count('id', filter=Q(is_correct=True)),
        )
    )
    result = []
    for row in rows:
        total = row['total']
        correct = row['correct']
        result.append({
            'subject_id': row['subject_id'],
            'subject_name': row['subject_name'],
            'total': total,
            'correct': correct,
            'accuracy_rate': round(correct / total, 4) if total else 0.0,
        })
    return result


class AnswerSubmitView(APIView):
    permission_classes = [IsChild]

    def post(self, request):
        serializer = AnswerSubmitSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        history = serializer.save()
        return Response(
            {'id': str(history.id), 'is_correct': history.is_correct},
            status=status.HTTP_201_CREATED,
        )


class ProgressSummaryView(APIView):
    permission_classes = [IsChild]

    def get(self, request):
        summary = _build_summary(request.user.child_profile)
        serializer = SubjectSummarySerializer(summary, many=True)
        return Response(serializer.data)


class ChildProgressSummaryView(APIView):
    permission_classes = [IsParent]

    def get(self, request, child_id):
        child_profile = get_object_or_404(ChildProfile, user__id=child_id)
        relation_exists = ParentChildRelation.objects.filter(
            parent=request.user.parent_profile,
            child=child_profile,
        ).exists()
        if not relation_exists:
            return Response(status=status.HTTP_404_NOT_FOUND)
        summary = _build_summary(child_profile)
        serializer = SubjectSummarySerializer(summary, many=True)
        return Response(serializer.data)
