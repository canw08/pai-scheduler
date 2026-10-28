from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Preset(models.Model):
    # 定义预设类型
    PRESET_TYPE_CHOICES = [
        ('preset_wace', 'WACE预设'),
        ('preset_ase', 'ASE预设'),
        ('preset_bse', 'BSE预设'),
        ('preset_art', 'ART预设'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='presets')
    preset_type = models.CharField(max_length=20, choices=PRESET_TYPE_CHOICES)
    data = models.JSONField()  # 用于存储动态数据（如老师列表、课程表等）
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'preset_type')  # 每个用户每种类型的 preset 只会有一份

    def __str__(self):
        return f'{self.user.username} - {self.preset_type}'
