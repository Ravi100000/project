from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('admin-portal/', views.admin_portal_view, name='admin-portal'),
    path('approve-user/<int:user_id>/', views.approve_user_view, name='approve-user'),
]
