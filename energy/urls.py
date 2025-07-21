from django.urls import path
from .views import energy_predictions, upload_csv

urlpatterns = [
    path('energy-predictions/', energy_predictions, name='energy_predictions'),
    path('upload-csv/', upload_csv, name='upload_csv'),
]
