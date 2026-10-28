from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


# Create your models here.
class User(AbstractUser):
    role = models.CharField(max_length=20, choices=[('admin', '管理员'), ('teacher', '老师'), ('student', '学生')],
                            default="teacher")

    groups = models.ManyToManyField(Group, related_name="user_set_custom", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="user_set_custom_permissions", blank=True)

    def __str__(self):
        return self.username
