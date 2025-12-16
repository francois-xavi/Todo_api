import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestTaskFilters:
    """Tests pour les filtres de tâches"""
    
    def test_filter_completed_tasks(self, authenticated_client, multiple_tasks):
        """Filtrer les tâches complétées"""
        url = reverse('task-list') + '?is_completed=true'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert all(item['is_completed'] for item in response.data['data'])
        assert len(response.data['data']) == 3
    
    def test_filter_incomplete_tasks(self, authenticated_client, multiple_tasks):
        """Filtrer les tâches non complétées"""
        url = reverse('task-list') + '?is_completed=false'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert all(not item['is_completed'] for item in response.data['data'])
        assert response.data['count'] == 2

