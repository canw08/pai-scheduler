from django.urls import path
from .views import ImportPresetView, ExportPresetView, DownloadPresetTemplateView

urlpatterns = [
    path('import/', ImportPresetView.as_view(), name='import_preset'),
    path('export/', ExportPresetView.as_view(), name='export_preset'),
    path('template/', DownloadPresetTemplateView.as_view(), name='download_template'),
]
