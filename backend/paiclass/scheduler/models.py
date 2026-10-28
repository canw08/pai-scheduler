# scheduler/models.py
from django.db import models


class SchedulingTask(models.Model):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending')  # pending, running, completed, failed
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    progress = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return f"Task for Project {self.project.id} - Status: {self.status}"
