import pytest
from accounts.serializers import (
    RegisterSerializer, LoginSerializer, 
    ChangePasswordSerializer, UserSerializer
)
from accounts.models import User


@pytest.mark.django_db
class TestRegisterSerializer:
    """Tests for RegisterSerializer"""
    
    def test_valid_data(self, user_data):
        """Test with valid data"""
        serializer = RegisterSerializer(data=user_data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.email == user_data['email'].lower()
        assert user.check_password(user_data['password'])
    
    def test_password_mismatch(self, user_data):
        """Test with password mismatch"""
        user_data['password2'] = 'Different123!'
        serializer = RegisterSerializer(data=user_data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
    
    def test_duplicate_email(self, user, user_data):
        """Test with duplicate email"""
        user_data['email'] = user.email
        serializer = RegisterSerializer(data=user_data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors


@pytest.mark.django_db
class TestUserSerializer:
    """Tests for UserSerializer"""
    
    def test_serialization(self, user):
        """Test the serialization of a user"""
        serializer = UserSerializer(user)
        assert serializer.data['email'] == user.email
        assert 'password' not in serializer.data
    
    def test_email_readonly(self, user):
        """Test that email is readonly"""
        data = {'email': 'newemail@test.com', 'first_name': 'Updated'}
        serializer = UserSerializer(user, data=data, partial=True)
        assert serializer.is_valid()
        updated_user = serializer.save()
        assert updated_user.email == user.email 
        assert updated_user.first_name == 'Updated'
