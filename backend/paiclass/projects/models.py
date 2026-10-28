# projects/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Project(models.Model):
    # 定义预设类型
    PROJECT_TYPE_CHOICES = [
        ('project_wace', 'WACE项目'),
        ('project_ase', 'ASE项目'),
        ('project_bse', 'BSE项目'),
        ('project_art', 'ART项目'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES)
    config = models.JSONField(default=dict, blank=True)
    table = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    isPublish = models.BooleanField(null=True,blank=True)
    def __str__(self):
        return self.name
