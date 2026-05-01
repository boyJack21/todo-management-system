from rest_framework import generics
from rest_framework import status
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .serializer import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ProjectSerializer,
    RegisterSerializer,
    SubtaskSerializer,
    TodoSerializer,
    UserSerializer,
)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Project, Subtask, Todo
from rest_framework import viewsets, permissions
from rest_framework.views import APIView




class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Todo.objects
            .filter(user=self.request.user)
            .select_related("project")
            .prefetch_related("subtasks")
        )

    def perform_create(self, serializer):
        max_position = (
            Todo.objects
            .filter(user=self.request.user)
            .order_by("-position")
            .values_list("position", flat=True)
            .first()
        )
        serializer.save(
            user=self.request.user,
            position=(max_position or 0) + 1,
        )


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SubtaskViewSet(viewsets.ModelViewSet):
    serializer_class = SubtaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subtask.objects.filter(todo__user=self.request.user)


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email__iexact=email).first()

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
            reset_url = f"{frontend_url.rstrip('/')}/password-reset-confirm/{uid}/{token}"
            context = {
                "user": user,
                "reset_url": reset_url,
            }

            subject = "Reset your Todo Management password"
            text_body = render_to_string("tasks/password_reset_email.txt", context)
            html_body = render_to_string("tasks/password_reset_email.html", context)

            email_message = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email_message.attach_alternative(html_body, "text/html")
            email_message.send()

        return Response(
            {"detail": "If an account exists for this email, reset instructions will be sent."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )


@api_view(["GET"])
def email_exists(request):
    """Return whether a user with the given email exists.

    Query params: ?email=foo@example.com
    Response: { "exists": true/false }
    """
    email = request.query_params.get("email")
    if not email:
        return Response({"detail": "email query param required"}, status=400)

    exists = User.objects.filter(email__iexact=email).exists()
    return Response({"exists": exists})
