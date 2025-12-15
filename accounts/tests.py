from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import User, OTPCode

class UserModelTest(TestCase):
    """Tests pour le modèle User"""
    
    def test_user_creation(self):
        """Test la création d'un utilisateur"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('TestPass123!'))
        self.assertFalse(user.is_email_verified)


class OTPModelTest(TestCase):
    """Tests pour le modèle OTPCode"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
    
    def test_otp_generation(self):
        """Test la génération automatique du code OTP"""
        otp = OTPCode.objects.create(user=self.user, purpose='password_reset')
        self.assertEqual(len(otp.code), 6)
        self.assertTrue(otp.code.isdigit())
    
    def test_otp_validity(self):
        """Test la validité du code OTP"""
        otp = OTPCode.objects.create(user=self.user, purpose='password_reset')
        self.assertTrue(otp.is_valid())
        
        otp.mark_as_used()
        self.assertFalse(otp.is_valid())


class AuthAPITest(APITestCase):
    """Tests pour l'API d'authentification"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.password_reset_request_url = reverse('password-reset-request')
        self.password_reset_verify_url = reverse('password-reset-verify')
        
        self.user_data = {
            'username': 'johndoe',
            'email': 'john@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        self.existing_user = User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='ExistingPass123!'
        )
    
    def test_register_success(self):
        """Test inscription réussie"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['user']['email'], 'john@example.com')
        
        # Vérifier que l'utilisateur existe
        self.assertTrue(User.objects.filter(email='john@example.com').exists())
    
    def test_register_password_mismatch(self):
        """Test inscription avec mots de passe différents"""
        data = self.user_data.copy()
        data['password2'] = 'DifferentPass123!'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_duplicate_email(self):
        """Test inscription avec email existant"""
        data = self.user_data.copy()
        data['email'] = 'existing@example.com'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_success(self):
        """Test connexion réussie"""
        login_data = {
            'email': 'existing@example.com',
            'password': 'ExistingPass123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
    
    def test_login_invalid_credentials(self):
        """Test connexion avec mauvais credentials"""
        login_data = {
            'email': 'existing@example.com',
            'password': 'WrongPassword123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_password_reset_request(self):
        """Test demande de réinitialisation de mot de passe"""
        data = {'email': 'existing@example.com'}
        response = self.client.post(self.password_reset_request_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier qu'un OTP a été créé
        self.assertTrue(OTPCode.objects.filter(user=self.existing_user, purpose='password_reset').exists())
    
    def test_password_reset_verify_success(self):
        """Test vérification OTP et reset password réussi"""
        # Créer un OTP
        otp = OTPCode.objects.create(
            user=self.existing_user,
            purpose='password_reset'
        )
        
        data = {
            'email': 'existing@example.com',
            'otp_code': otp.code,
            'new_password': 'NewSecurePass123!',
            'new_password2': 'NewSecurePass123!'
        }
        response = self.client.post(self.password_reset_verify_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que le mot de passe a été changé
        self.existing_user.refresh_from_db()
        self.assertTrue(self.existing_user.check_password('NewSecurePass123!'))
        
        # Vérifier que l'OTP est marqué comme utilisé
        otp.refresh_from_db()
        self.assertTrue(otp.is_used)
    
    def test_password_reset_verify_invalid_otp(self):
        """Test vérification avec OTP invalide"""
        data = {
            'email': 'existing@example.com',
            'otp_code': '999999',
            'new_password': 'NewSecurePass123!',
            'new_password2': 'NewSecurePass123!'
        }
        response = self.client.post(self.password_reset_verify_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_profile_authenticated(self):
        """Test accès au profil utilisateur authentifié"""
        self.client.force_authenticate(user=self.existing_user)
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'existing@example.com')
    
    def test_user_profile_unauthenticated(self):
        """Test accès au profil sans authentification"""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)