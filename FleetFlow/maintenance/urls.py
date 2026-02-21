from django.urls import path
from . import views

urlpatterns = [
    path('', views.MaintenanceListView.as_view(), name='maintenance-list'),
    path('new/', views.MaintenanceCreateView.as_view(), name='maintenance-create'),
]
