from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action as action_decorator
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task
from .serializers import TaskSerializer
from .filters import TaskFilter

class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for all Crud opération on Task model
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter
    
    def get_queryset(self):
        """Get queryset for the current user"""
        return Task.objects.filter(author=self.request.user)
    
    @action_decorator(detail=True, methods=['post'], url_name='toggle-complete', url_path='toggle-complete')
    def toggle_complete(self, request, pk=None):
        """custom action to toggle the completion status of a task"""
        task = self.get_object()
        task.is_completed = not task.is_completed
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)