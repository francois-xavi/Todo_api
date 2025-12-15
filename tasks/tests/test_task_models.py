import pytest
from tasks.models import Task


@pytest.mark.django_db
class TestTaskModel:
    """Tests pour le modèle Task"""
    
    def test_create_task(self, user):
        """Création d'une tâche"""
        task = Task.objects.create(
            title='Ma tâche',
            description='Description',
            author=user
        )
        
        assert task.title == 'Ma tâche'
        assert task.description == 'Description'
        assert task.is_completed is False
        assert task.author == user
        assert task.created_at is not None
    
    def test_task_str_incomplete(self, user):
        """Représentation string d'une tâche non complétée"""
        task = Task.objects.create(
            title='Tâche test',
            author=user,
            is_completed=False
        )
        
        assert str(task) == '○ Tâche test'
    
    def test_task_str_complete(self, user):
        """Représentation string d'une tâche complétée"""
        task = Task.objects.create(
            title='Tâche test',
            author=user,
            is_completed=True
        )
        
        assert str(task) == '✓ Tâche test'
    
    def test_task_ordering(self, user):
        """Les tâches sont ordonnées par date de création décroissante"""
        task1 = Task.objects.create(title='Première', author=user)
        task2 = Task.objects.create(title='Deuxième', author=user)
        task3 = Task.objects.create(title='Troisième', author=user)
        
        tasks = list(Task.objects.all())
        assert tasks[0] == task3
        assert tasks[1] == task2
        assert tasks[2] == task1
    
    def test_task_author_deletion(self, user):
        """Supprimer l'auteur supprime ses tâches (CASCADE)"""
        task = Task.objects.create(title='Test', author=user)
        user_id = user.id
        task_id = task.id
        
        user.delete()
        
        assert not Task.objects.filter(id=task_id).exists()
