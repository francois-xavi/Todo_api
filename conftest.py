import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from tasks.models import Task

User = get_user_model()


@pytest.fixture
def api_client():
    """Fixture pour le client API"""
    return APIClient()


@pytest.fixture
def user(db):
    """Fixture pour créer un utilisateur de test"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123!',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Fixture pour un client authentifié"""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def task(db):
    """Fixture pour créer une tâche de test"""
    return Task.objects.create(
        title='Test Task',
        description='Test Description',
        is_completed=False
    )


@pytest.fixture
def multiple_tasks(db):
    """Fixture pour créer plusieurs tâches"""
    tasks = []
    for i in range(5):
        task = Task.objects.create(
            title=f'Task {i+1}',
            description=f'Description {i+1}',
            is_completed=i % 2 == 0
        )
        tasks.append(task)
    return tasks