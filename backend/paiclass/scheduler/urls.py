# scheduler/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('fitness/', views.project_checkFitness),
    path('run/', views.project_run),  # 启动排课任务
    path('run/status/', views.project_run_status),  # 查询排课任务状态
]
