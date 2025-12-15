import pytest
from django.urls import reverse
from rest_framework import status
from accounts.models import User


@pytest.mark.django_db
class TestRegister:
    """Tests pour l'enregistrement utilisateur"""
    
    def test_register_success(self, api_client, user_data):
        """Test enregistrement réussi"""
        url = reverse('auth-register')
        response = api_client.post(url, user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email=user_data['email']).exists()
        assert 'password' not in response.data
    
    def test_register_password_mismatch(self, api_client, user_data):
        """Test avec mots de passe non correspondants"""
        url = reverse('auth-register')
        user_data['password2'] = 'DifferentPass123!'
        response = api_client.post(url, user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data
    
    def test_register_duplicate_email(self, api_client, user, user_data):
        """Test avec email déjà utilisé"""
        url = reverse('auth-register')
        user_data['email'] = user.email
        response = api_client.post(url, user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
    
    def test_register_weak_password(self, api_client, user_data):
        """Test avec mot de passe faible"""
        url = reverse('auth-register')
        user_data['password'] = '123'
        user_data['password2'] = '123'
        response = api_client.post(url, user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data
    
    def test_register_missing_required_fields(self, api_client):
        """Test avec champs requis manquants"""
        url = reverse('auth-register')
        response = api_client.post(url, {'email': 'test@test.com'})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data