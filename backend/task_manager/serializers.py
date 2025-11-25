from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class TaskAnalysisSerializer(serializers.Serializer):
    tasks = serializers.ListField(child=serializers.DictField())
    strategy = serializers.CharField(default='smart_balance')


class TaskWithScoreSerializer(serializers.Serializer):
    title = serializers.CharField()
    due_date = serializers.DateField()
    estimated_hours = serializers.FloatField()
    importance = serializers.IntegerField()
    dependencies = serializers.ListField(default=list)
    priority_score = serializers.FloatField()
    explanation = serializers.CharField()