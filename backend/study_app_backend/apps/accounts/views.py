from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, ParentChildRelation
from .permissions import IsParent
from .serializers import (
    ChildRegisterSerializer,
    ParentRegisterSerializer,
    ChildProfileSerializer,
    ParentProfileSerializer,
    ChildSummarySerializer,
    ParentChildRelationCreateSerializer,
)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        return data


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ChildRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ChildRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'id': str(user.id), 'username': user.username, 'role': user.role},
            status=status.HTTP_201_CREATED,
        )


class ParentRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ParentRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'id': str(user.id), 'username': user.username, 'role': user.role},
            status=status.HTTP_201_CREATED,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()
        except TokenError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_serializer(self, user, *args, **kwargs):
        if user.role == User.ROLE_CHILD:
            return ChildProfileSerializer(user.child_profile, *args, **kwargs)
        return ParentProfileSerializer(user.parent_profile, *args, **kwargs)

    def get(self, request):
        serializer = self._get_serializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = self._get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ParentChildrenView(APIView):
    permission_classes = [IsParent]

    def get(self, request):
        relations = ParentChildRelation.objects.filter(
            parent=request.user.parent_profile
        ).select_related('child__user')
        children = [r.child for r in relations]
        serializer = ChildSummarySerializer(children, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ParentChildRelationCreateSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)


class ParentChildDetailView(APIView):
    permission_classes = [IsParent]

    def delete(self, request, child_id):
        try:
            relation = ParentChildRelation.objects.get(
                parent=request.user.parent_profile,
                child__user__id=child_id,
            )
        except ParentChildRelation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
