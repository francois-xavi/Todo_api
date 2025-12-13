import pytest
from django.urls import reverse
from rest_framework import status
from tasks.models import Task


def get_results(response):
    """Helper for pagination"""
    if isinstance(response.data, dict) and 'results' in response.data:
        return response.data['results']
    return response.data


@pytest.mark.django_db
class TestTaskModel:
    """Tests for the Task model"""
    
    def test_task_creation(self, task):
        """Test task creation"""
        assert task.title == 'Test Task'
        assert task.description == 'Test Description'
        assert task.is_completed is False
        assert task.created_at is not None
        assert task.updated_at is not None
    
    def test_task_str_representation(self, task):
        """Test task string representation"""
        assert 'Test Task' in str(task)
        assert '○' in str(task)  # Non complétée
    
    def test_task_completed_str(self, task):
        """Test task completed string representation"""
        task.is_completed = True
        task.save()
        assert '✓' in str(task)
    
    def test_task_ordering(self, multiple_tasks):
        """Test task ordering (most recent first)"""
        tasks = Task.objects.order_by('-created_at')
        assert tasks[0].title == 'Task 5'
        assert tasks[4].title == 'Task 1'


@pytest.mark.django_db
class TestTaskListAPI:
    """Tests for GET /api/tasks/"""
    
    def test_list_tasks_empty(self, api_client):
        """Test list empty tasks"""
        url = reverse('task-list')
        response = api_client.get(url)
        results = get_results(response)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(results['data']) == 0
    
    def test_list_tasks(self, api_client, multiple_tasks):
        """Test list all tasks"""
        url = reverse('task-list')
        response = api_client.get(url)
        results = get_results(response)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(results['data']) == 5
    
    def test_filter_completed_tasks(self, api_client, multiple_tasks):
        """Test filter completed tasks"""
        url = reverse('task-list')
        response = api_client.get(url, {'is_completed': 'true'})
        results = get_results(response)
        
        assert response.status_code == status.HTTP_200_OK
        completed_count = sum(1 for task in results['data'] if task['is_completed'])
        assert completed_count == 3  # Tasks 1, 3, 5 (indices 0, 2, 4)
    
    def test_filter_uncompleted_tasks(self, api_client, multiple_tasks):
        """Test filter uncompleted tasks"""
        url = reverse('task-list')
        response = api_client.get(url, {'is_completed': 'false'})
        results = get_results(response)
        
        assert response.status_code == status.HTTP_200_OK
        uncompleted_count = sum(1 for task in results['data'] if not task['is_completed'])
        assert uncompleted_count == 2  # Tasks 2, 4 (indices 1, 3)


@pytest.mark.django_db
class TestTaskCreateAPI:
    """Tests for POST /api/tasks/"""
    
    def test_create_task_success(self, api_client):
        """Test create task success"""
        url = reverse('task-list')
        data = {
            'title': 'Nouvelle Tâche',
            'description': 'Description de la tâche',
            'is_completed': False
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Nouvelle Tâche'
        assert 'id' in response.data
        assert 'created_at' in response.data
        assert Task.objects.count() == 1
    
    def test_create_task_without_title(self, api_client):
        """Test create task without title (should fail)"""
        url = reverse('task-list')
        data = {'description': 'Sans titre'}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data
    
    def test_create_task_with_empty_title(self, api_client):
        """Test create task with empty title (should fail)"""
        url = reverse('task-list')
        data = {'title': '   ', 'description': 'Test'}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_task_minimal(self, api_client):
        """Test create task with minimal data"""
        url = reverse('task-list')
        data = {'title': 'Tâche Minimale'}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['description'] is None or response.data['description'] == ''
        assert response.data['is_completed'] is False


@pytest.mark.django_db
class TestTaskRetrieveAPI:
    """Tests for GET /api/tasks/{id}/"""
    
    def test_retrieve_task(self, api_client, task):
        """Test retrieve specific task"""
        url = reverse('task-detail', kwargs={'pk': task.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Test Task'
        assert str(response.data['id']) == str(task.pk)
    
    def test_retrieve_nonexistent_task(self, api_client):
        """Test retrieve nonexistent task"""
        url = reverse('task-detail', kwargs={'pk': 99999})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestTaskUpdateAPI:
    """Tests for PUT/PATCH /api/tasks/{id}/"""
    
    def test_update_task_put(self, api_client, task):
        """Test update task (PUT)"""
        url = reverse('task-detail', kwargs={'pk': task.pk})
        data = {
            'title': 'Tâche Modifiée',
            'description': 'Description modifiée',
            'is_completed': True
        }
        response = api_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.title == 'Tâche Modifiée'
        assert task.is_completed is True
    
    def test_partial_update_task_patch(self, api_client, task):
        """Test partial update task (PATCH)"""
        url = reverse('task-detail', kwargs={'pk': task.pk})
        data = {'is_completed': True}
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.is_completed is True
        assert task.title == 'Test Task'
    
    def test_update_task_title_only(self, api_client, task):
        """Test update task title only"""
        url = reverse('task-detail', kwargs={'pk': task.pk})
        data = {'title': 'Nouveau Titre'}
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.title == 'Nouveau Titre'
        assert task.description == 'Test Description'


@pytest.mark.django_db
class TestTaskDeleteAPI:
    """Tests for DELETE /api/tasks/{id}/"""
    
    def test_delete_task(self, api_client, task):
        """Test delete task"""
        url = reverse('task-detail', kwargs={'pk': task.pk})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Task.objects.count() == 0
    
    def test_delete_nonexistent_task(self, api_client):
        """Test delete nonexistent task"""
        url = reverse('task-detail', kwargs={'pk': 99999})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestToggleCompleteAction:
    """Tests for the toggle_complete action"""
    
    def test_toggle_complete_from_false_to_true(self, api_client, task):
        """Test toggle complete from false to true"""
        url = reverse('task-toggle-complete', kwargs={'pk': task.pk})
        initial_status = task.is_completed
        
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.is_completed is not initial_status
        assert task.is_completed is True
        
    def test_toggle_complete_from_true_to_false(self, api_client, task):
        """Test toggle complete from true to false"""
        task.is_completed = True
        task.save()
        
        url = reverse('task-toggle-complete', kwargs={'pk': task.pk})
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.is_completed is False
    
    def test_toggle_complete_multiple_times(self, api_client, task):
        """Test toggle complete multiple times"""
        url = reverse('task-toggle-complete', kwargs={'pk': task.pk})
        
        # Premier toggle
        api_client.post(url)
        task.refresh_from_db()
        assert task.is_completed is True
        
        # Deuxième toggle
        api_client.post(url)
        task.refresh_from_db()
        assert task.is_completed is False
        
        # Troisième toggle
        api_client.post(url)
        task.refresh_from_db()
        assert task.is_completed is True


@pytest.mark.django_db
class TestTaskValidation:
    """Tests for data validation"""
    
    def test_title_max_length(self, api_client):
        """Test title max length validation"""
        url = reverse('task-list')
        data = {'title': 'A' * 201}  # Plus que 200 caractères
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_title_whitespace_trimmed(self, api_client):
        """Test title whitespace trimmed"""
        url = reverse('task-list')
        data = {'title': '  Titre avec espaces  '}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Titre avec espaces'