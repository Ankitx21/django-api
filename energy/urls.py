from django.urls import path
from . import views

urlpatterns = [
    path('energy-predictions/', views.energy_predictions, name='energy_predictions'),
]