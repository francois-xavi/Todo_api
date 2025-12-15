import pytest
from tasks.serializers import TaskSerializer
from tasks.models import Task


@pytest.mark.django_db
class TestTaskSerializer:
    """Tests pour TaskSerializer"""
    
    def test_serializer_with_valid_data(self, user, rf):
        """Sérialisation avec données valides"""
        request = rf.post('/')
        request.user = user
        
        data = {
            'title': 'Nouvelle tâche',
            'description': 'Description test',
            'is_completed': False
        }
        serializer = TaskSerializer(data=data, context={'request': request})
        
        assert serializer.is_valid()
        task = serializer.save()
        assert task.title == 'Nouvelle tâche'
        assert task.author == user
    
    def test_serializer_strips_title(self, user, rf):
        """Le titre est nettoyé des espaces"""
        request = rf.post('/')
        request.user = user
        
        data = {'title': '  Titre avec espaces  '}
        serializer = TaskSerializer(data=data, context={'request': request})
        
        assert serializer.is_valid()
        task = serializer.save()
        assert task.title == 'Titre avec espaces'
    
    def test_serializer_empty_title(self):
        """Validation échoue si le titre est vide"""
        data = {'title': '   '}
        serializer = TaskSerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'title' in serializer.errors
    
    def test_serializer_readonly_fields(self, task):
        """Les champs en lecture seule ne peuvent pas être modifiés"""
        original_created = task.created_at
        data = {
            'title': 'Modifié',
            'created_at': '2020-01-01T00:00:00Z',
            'id': 99999
        }
        serializer = TaskSerializer(task, data=data, partial=True)
        
        assert serializer.is_valid()
        updated_task = serializer.save()
        assert updated_task.id == task.id
        assert updated_task.created_at == original_created
    
    def test_serializer_output(self, task):
        """Test la sérialisation d'une tâche existante"""
        serializer = TaskSerializer(task)
        data = serializer.data
        
        assert data['id'] == str(task.id)
        assert data['title'] == task.title
        assert data['description'] == task.description
        assert data['is_completed'] == task.is_completed
        assert 'created_at' in data
        assert 'updated_at' in data
        