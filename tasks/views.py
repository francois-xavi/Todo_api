from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action as action_decorator
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task
from .serializers import TaskSerializer
from .filters import TaskFilter
from rest_framework import permissions

class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for all Crud opération on Task model
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get queryset for the current user"""
        return Task.objects.filter(author=self.request.user)
    