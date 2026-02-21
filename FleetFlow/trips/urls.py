from django.urls import path
from . import views

urlpatterns = [
    path('', views.TripListView.as_view(), name='trip-list'),
    path('new/', views.TripCreateView.as_view(), name='trip-create'),
    path('<int:pk>/', views.TripDetailView.as_view(), name='trip-detail'),
    path('<int:pk>/edit/', views.TripUpdateView.as_view(), name='trip-edit'),
]
