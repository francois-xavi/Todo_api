from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    """
    Task serializer
    """
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'is_completed', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_title(self, value):
        """Validate the title"""
        if not value or not value.strip():
            raise serializers.ValidationError("Le titre ne peut pas être vide")
        return value.strip()
    
    def validate(self, data):
        """Validate the data"""
        if 'description' in data and data['description']:
            data['description'] = data['description'].strip()
        return data


    def create(self, validated_data):
        """Create a task"""
        user = self.context['request'].user
        validated_data['author'] = user
        return Task.objects.create(**validated_data)