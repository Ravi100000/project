from django.urls import path
from . import views

urlpatterns = [
    path('', views.DriverListView.as_view(), name='driver-list'),
    path('new/', views.DriverCreateView.as_view(), name='driver-create'),
    path('<int:pk>/edit/', views.DriverUpdateView.as_view(), name='driver-edit'),
    path('<int:pk>/delete/', views.DriverDeleteView.as_view(), name='driver-delete'),
]
