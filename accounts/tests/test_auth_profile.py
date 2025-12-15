import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestProfile:
    """Tests pour le profil utilisateur"""
    def test_get_profile_authenticated(self, authenticated_client, user):
        """Test récupération profil authentifié"""
        url = reverse('auth-me')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
        assert response.data['first_name'] == user.first_name
    
    def test_get_profile_unauthenticated(self, api_client):
        """Test récupération profil non authentifié"""
        url = reverse('auth-me')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_profile_success(self, authenticated_client, user):
        """Test update profile"""
        url = reverse('auth-update-me')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+229987654321'
        }
        response = authenticated_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'Name'
        
        # Vérifier en DB
        user.refresh_from_db()
        assert user.first_name == 'Updated'
    
    def test_update_profile_readonly_fields(self, authenticated_client, user):
        """Test update profile readonly fields"""
        url = reverse('auth-update-me')
        original_email = user.email
        data = {'email': 'newemail@example.com'}
        response = authenticated_client.patch(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.email == original_email

