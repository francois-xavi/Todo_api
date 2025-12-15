import pytest
from django.urls import reverse
from rest_framework import status
from tasks.models import Task


@pytest.mark.django_db
class TestTaskList:
    """Tests for the list of tasks"""
    
    def test_list_tasks_authenticated(self, authenticated_client, multiple_tasks):
        """the list of tasks is retrieved successfully"""
        url = reverse('task-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 5
    
    def test_list_tasks_unauthenticated(self, api_client):
        """the list of tasks is not retrieved if the user is not authenticated"""
        url = reverse('task-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_only_own_tasks(self, authenticated_client, task, other_user_task):
        """the user can only see his own tasks"""
        url = reverse('task-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['title'] == task.title
    
    def test_empty_task_list(self, authenticated_client):
        """the list is empty if there are no tasks"""
        url = reverse('task-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 0


@pytest.mark.django_db
class TestTaskCreate:
    """Tests pour la création de tâches"""
    
    def test_create_task_success(self, authenticated_client, task_data, user):
        """the task is created successfully"""
        url = reverse('task-list')
        response = authenticated_client.post(url, task_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == task_data['title']
        assert response.data['description'] == task_data['description']
        assert response.data['is_completed'] is False
        
        # Vérifier en DB
        task = Task.objects.get(id=response.data['id'])
        assert task.author == user
    
    def test_create_task_minimal_data(self, authenticated_client, user):
        """the task is created successfully with minimal data (only title)"""
        url = reverse('task-list')
        data = {'title': 'Tâche simple'}
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Tâche simple'
        assert response.data['description'] in [None, '']
        assert response.data['is_completed'] is False
    
    def test_create_task_empty_title(self, authenticated_client):
        """the task is not created if the title is empty"""
        url = reverse('task-list')
        data = {'title': '   ', 'description': 'Test'}
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data
    
    def test_create_task_missing_title(self, authenticated_client):
        """the task is not created if the title is missing"""
        url = reverse('task-list')
        data = {'description': 'Sans titre'}
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data
    
    def test_create_task_strips_whitespace(self, authenticated_client):
        """the whitespace is stripped from the title and description"""
        url = reverse('task-list')
        data = {
            'title': '  Titre avec espaces  ',
            'description': '  Description avec espaces  '
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Titre avec espaces'
        assert response.data['description'] == 'Description avec espaces'
    
    def test_create_task_unauthenticated(self, api_client, task_data):
        """the task is not created if the user is not authenticated"""
        url = reverse('task-list')
        response = api_client.post(url, task_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTaskRetrieve:
    """Tests for the retrieval of a task"""
    
    def test_retrieve_task_success(self, authenticated_client, task):
        """the task is retrieved successfully"""
        url = reverse('task-detail', kwargs={'pk': task.pk})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(task.id)
        assert response.data['title'] == task.title
    
    def test_retrieve_other_user_task(self, authenticated_client, other_user_task):
        """the task is not retrieved if the user is not the owner"""
        url = reverse('task-detail', kwargs={'pk': other_user_task.pk})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_retrieve_nonexistent_task(self, authenticated_client):
        """the task is not retrieved if the task does not exist"""
        url = reverse('task-detail', kwargs={'pk': 99999})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestTaskUpdate:
    """Tests for the update of a task"""
    
    def test_update_task_full(self, authenticated_client, task):
        """the task is updated successfully"""
        url = reverse('task-detail', kwargs={'pk': task.pk})
        data = {
            'title': 'Titre modifié',
            'description': 'Description modifiée',
            'is_completed': True
        }
        response = authenticated_client.put(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Titre modifié'
        assert response.data['description'] == 'Description modifiée'
        assert response.data['is_completed'] is True
        
        # Vérifier en DB
        task.refresh_from_db()
        assert task.title == 'Titre modifié'
        assert task.is_completed is True
    
    def test_update_task_partial(self, authenticated_client, task):
        """the task is updated successfully"""
        url = reverse('task-detail', kwargs={'pk': task.pk})
        original_description = task.description
        data = {'title': 'Nouveau titre'}
        response = authenticated_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Nouveau titre'
        assert response.data['description'] == original_description
    
    def test_update_task_completion_status(self, authenticated_client, task):
        """the task completion status is updated successfully"""
        url = reverse('task-detail', kwargs={'pk': task.pk})
        data = {'is_completed': True}
        response = authenticated_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_completed'] is True
        
        task.refresh_from_db()
        assert task.is_completed is True
    
    def test_update_other_user_task(self, authenticated_client, other_user_task):
        """the task is not updated if the user is not the owner"""
        url = reverse('task-detail', kwargs={'pk': other_user_task.pk})
        data = {'title': 'Tentative de modification'}
        response = authenticated_client.patch(url, data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        other_user_task.refresh_from_db()
        assert other_user_task.title != 'Tentative de modification'
    
    def test_update_readonly_fields(self, authenticated_client, task):
        """the readonly fields are not updated"""
        url = reverse('task-detail', kwargs={'pk': task.pk})
        original_created = task.created_at
        data = {
            'title': 'Titre modifié',
            'created_at': '2020-01-01T00:00:00Z'
        }
        response = authenticated_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.created_at == original_created


@pytest.mark.django_db
class TestTaskDelete:
    """Tests for the deletion of a task"""
    
    def test_delete_task_success(self, authenticated_client, task):
        """the task is deleted successfully"""
        url = reverse('task-detail', kwargs={'pk': task.pk})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(id=task.id).exists()
    
    def test_delete_other_user_task(self, authenticated_client, other_user_task):
        """the task is not deleted if the user is not the owner"""
        url = reverse('task-detail', kwargs={'pk': other_user_task.pk})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Task.objects.filter(id=other_user_task.id).exists()
    
    def test_delete_nonexistent_task(self, authenticated_client):
        """the task is not deleted if the task does not exist"""
        url = reverse('task-detail', kwargs={'pk': 99999})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

