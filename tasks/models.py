from django.db import models
from core.utils.abstract_models import BaseModel

class Task(BaseModel):
    """
    Task model
    """
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
