from django.urls import path
from . import views

urlpatterns = [
    path('', views.ExpenseListView.as_view(), name='expense-list'),
    path('new/', views.ExpenseCreateView.as_view(), name='expense-create'),
]
