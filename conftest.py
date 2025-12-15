import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """An unauthorized api client"""
    return APIClient()


@pytest.fixture
def user(db):
    """A test user"""
    return User.objects.create_user(
        email='test@example.com',
        password='TestPass123!',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """An authorized api client"""
    api_client.force_authenticate(user=user)
    return api_client