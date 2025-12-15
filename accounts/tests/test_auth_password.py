import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestChangePassword:
    """Tests pour changement de mot de passe"""
    
    def test_change_password_success(self, authenticated_client, user):
        """Test changement de mot de passe réussi"""
        url = reverse('auth-change-password')
        data = {
            'old_password': 'TestPass123!',
            'new_password': 'NewSecurePass123!',
            'new_password2': 'NewSecurePass123!'
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Vérifier que le nouveau mot de passe fonctionne
        user.refresh_from_db()
        assert user.check_password('NewSecurePass123!')
    
    def test_change_password_wrong_old_password(self, authenticated_client):
        """Test avec mauvais ancien mot de passe"""
        url = reverse('auth-change-password')
        data = {
            'old_password': 'WrongPassword123!',
            'new_password': 'NewSecurePass123!',
            'new_password2': 'NewSecurePass123!'
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_change_password_mismatch(self, authenticated_client):
        """Test avec nouveaux mots de passe non correspondants"""
        url = reverse('auth-change-password')
        data = {
            'old_password': 'TestPass123!',
            'new_password': 'NewSecurePass123!',
            'new_password2': 'DifferentPass123!'
        }
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPasswordReset:
    """Tests pour réinitialisation de mot de passe"""
    
    def test_reset_password_request_success(self, api_client, user):
        """Test demande de réinitialisation réussie"""
        url = reverse('auth-reset-password')
        data = {'email': user.email}
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        
        # Vérifier qu'un OTP a été créé
        from accounts.models import OTPCode
        assert OTPCode.objects.filter(user=user, is_used=False).exists()
    
    def test_reset_password_nonexistent_email(self, api_client):
        """Test avec email inexistant"""
        url = reverse('auth-reset-password')
        data = {'email': 'nonexistent@example.com'}
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_verify_reset_success(self, api_client, user, otp_code):
        """Test vérification OTP et réinitialisation réussie"""
        url = reverse('auth-verify-reset')
        data = {
            'email': user.email,
            'otp_code': otp_code.code,
            'new_password': 'NewSecurePass123!',
            'new_password2': 'NewSecurePass123!'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Vérifier le nouveau mot de passe
        user.refresh_from_db()
        assert user.check_password('NewSecurePass123!')
        
        # Vérifier que l'OTP est marqué comme utilisé
        otp_code.refresh_from_db()
        assert otp_code.is_used is True
    
    def test_verify_reset_invalid_otp(self, api_client, user):
        """Test avec OTP invalide"""
        url = reverse('auth-verify-reset')
        data = {
            'email': user.email,
            'otp_code': '999999',
            'new_password': 'NewSecurePass123!',
            'new_password2': 'NewSecurePass123!'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_verify_reset_expired_otp(self, api_client, user, expired_otp):
        """Test avec OTP expiré"""
        url = reverse('auth-verify-reset')
        data = {
            'email': user.email,
            'otp_code': expired_otp.code,
            'new_password': 'NewSecurePass123!',
            'new_password2': 'NewSecurePass123!'
        }
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST