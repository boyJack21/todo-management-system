from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from .models import Project, Subtask, Todo


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "date_joined"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "email"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"]
        )
        return user
    

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "color", "created_at"]
        read_only_fields = ["id", "created_at"]


class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = ["id", "todo", "title", "completed", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_todo(self, value):
        request = self.context.get("request")

        if request and value.user != request.user:
            raise serializers.ValidationError("Invalid todo.")

        return value


class TodoSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        source="project",
        required=False,
        allow_null=True,
        write_only=True,
    )
    subtasks = SubtaskSerializer(many=True, read_only=True)

    class Meta:
        model = Todo
        fields = "__all__"
        read_only_fields = ["id", "user", "created_at", "project", "subtasks"]

    def validate_project(self, value):
        request = self.context.get("request")

        if value and request and value.user != request.user:
            raise serializers.ValidationError("Invalid project.")

        return value

    def validate(self, attrs):
        status_value = attrs.get("status")
        completed_value = attrs.get("completed")

        if status_value == Todo.STATUS_DONE:
            attrs["completed"] = True
        elif completed_value is True:
            attrs["status"] = Todo.STATUS_DONE
        elif completed_value is False and status_value == Todo.STATUS_DONE:
            attrs["status"] = Todo.STATUS_BACKLOG

        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs["uid"]))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid password reset link.")

        if not default_token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError("Invalid or expired password reset link.")

        attrs["user"] = user
        return attrs

    def save(self):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
