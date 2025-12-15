from django.db import models
from core.utils.abstract_models import BaseModel
from django.contrib.auth import get_user_model
User = get_user_model()

class Task(BaseModel):
    """
    Task model
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks', help_text="Auteur de la tâche", null=True, blank=True)
    title = models.CharField(max_length=200, help_text="Titre de la tâche")
    description = models.TextField(blank=True, null=True, help_text="Description détaillée")
    is_completed = models.BooleanField(default=False, help_text="Statut de complétion")


    class Meta:
        ordering = ['-created_at']
        verbose_name = "Tâche"
        verbose_name_plural = "Tâches"

    def __str__(self):
        status = "✓" if self.is_completed else "○"
        return f"{status} {self.title}"
