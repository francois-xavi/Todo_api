import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestLogin:
    """Tests pour la connexion utilisateur"""
    
    def test_login_success(self, api_client, user):
        """Test connexion réussie"""
        url = reverse('auth-login')
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.data
        assert 'refresh_token' in response.data
    
    def test_login_wrong_password(self, api_client, user):
        """Test avec mauvais mot de passe"""
        url = reverse('auth-login')
        data = {
            'email': 'test@example.com',
            'password': 'WrongPassword123!'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_nonexistent_user(self, api_client):
        """Test avec utilisateur inexistant"""
        url = reverse('auth-login')
        data = {
            'email': 'nonexistent@example.com',
            'password': 'TestPass123!'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_missing_credentials(self, api_client):
        """Test avec identifiants manquants"""
        url = reverse('auth-login')
        response = api_client.post(url, {})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data or 'password' in response.data
