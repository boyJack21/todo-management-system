from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Project, Todo


class TodoApiIsolationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="owner@example.com",
            email="owner@example.com",
            password="StrongPassword123!",
        )
        self.other_user = User.objects.create_user(
            username="other@example.com",
            email="other@example.com",
            password="StrongPassword123!",
        )
        self.project = Project.objects.create(user=self.user, name="Personal")
        self.other_project = Project.objects.create(user=self.other_user, name="Private")
        self.todo = Todo.objects.create(user=self.user, project=self.project, title="My task")
        Todo.objects.create(user=self.other_user, project=self.other_project, title="Other task")

        access = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_todo_list_only_returns_authenticated_users_data(self):
        response = self.client.get("/api/todos/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "My task")

    def test_user_cannot_assign_todo_to_another_users_project(self):
        response = self.client.patch(
            f"/api/todos/{self.todo.id}/",
            {"project_id": self.other_project.id},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.project_id, self.project.id)

    def test_project_list_only_returns_authenticated_users_projects(self):
        response = self.client.get("/api/projects/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Personal")
