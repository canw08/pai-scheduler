# projects/urls.py
from django.urls import path
from . import views
from .views import ProjectListView

urlpatterns = [
    path('list/', ProjectListView.as_view()),
    path('get/', views.project_get),
    path('create/', views.project_create),
    path('edit/', views.project_edit),
    path('delete/', views.project_delete),
]
