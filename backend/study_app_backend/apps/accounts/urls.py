from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ChildRegisterView,
    ParentRegisterView,
    LoginView,
    LogoutView,
    MeView,
    ParentChildrenView,
    ParentChildDetailView,
)

urlpatterns = [
    path('auth/register/child/', ChildRegisterView.as_view()),
    path('auth/register/parent/', ParentRegisterView.as_view()),
    path('auth/login/', LoginView.as_view()),
    path('auth/token/refresh/', TokenRefreshView.as_view()),
    path('auth/logout/', LogoutView.as_view()),
    path('users/me/', MeView.as_view()),
    path('parents/me/children/', ParentChildrenView.as_view()),
    path('parents/me/children/<uuid:child_id>/', ParentChildDetailView.as_view()),
]
