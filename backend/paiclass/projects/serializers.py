# projects/serializers.py
from rest_framework import serializers
from .models import Project


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'project_type', 'created_at']


class ProjectDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'project_type', 'config', 'table', 'created_at']
