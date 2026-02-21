from django.urls import path
from . import views

urlpatterns = [
    path('', views.VehicleListView.as_view(), name='vehicle-list'),
    path('new/', views.VehicleCreateView.as_view(), name='vehicle-create'),
    path('<int:pk>/edit/', views.VehicleUpdateView.as_view(), name='vehicle-edit'),
    path('<int:pk>/delete/', views.VehicleDeleteView.as_view(), name='vehicle-delete'),
]
