"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from tasks.views import (
    CurrentUserView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    ProjectViewSet,
    RegisterView,
    SubtaskViewSet,
    TodoViewSet,
    email_exists,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'todos', TodoViewSet, basename='todo')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'subtasks', SubtaskViewSet, basename='subtask')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/me/", CurrentUserView.as_view(), name="current_user"),
    path("api/email-exists/", email_exists, name="email_exists"),
    path("api/password-reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path("api/password-reset-confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("api/", include(router.urls)),
]
