import pytest
from tasks.models import Task

from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def another_user(db):
    """Second utilisateur pour tests de permissions"""
    return User.objects.create_user(
        email='another@example.com',
        password='TestPass123!',
        first_name='Another',
        last_name='User'
    )

@pytest.fixture
def task_data():
    """Données valides pour créer une tâche"""
    return {
        'title': 'Ma nouvelle tâche',
        'description': 'Description de la tâche',
        'is_completed': False
    }


@pytest.fixture
def task(user):
    """Crée une tâche de test"""
    return Task.objects.create(
        title='Tâche de test',
        description='Description test',
        is_completed=False,
        author=user
    )


@pytest.fixture
def completed_task(user):
    """Crée une tâche complétée"""
    return Task.objects.create(
        title='Tâche complétée',
        description='Déjà terminée',
        is_completed=True,
        author=user
    )


@pytest.fixture
def multiple_tasks(user):
    """Crée plusieurs tâches pour les tests de liste"""
    tasks = []
    for i in range(5):
        tasks.append(
            Task.objects.create(
                title=f'Tâche {i+1}',
                description=f'Description {i+1}',
                is_completed=i % 2 == 0,
                author=user
            )
        )
    return tasks


@pytest.fixture
def other_user_task(another_user):
    """Crée une tâche appartenant à un autre utilisateur"""
    return Task.objects.create(
        title='Tâche autre utilisateur',
        description='Pas accessible',
        is_completed=False,
        author=another_user
    )
