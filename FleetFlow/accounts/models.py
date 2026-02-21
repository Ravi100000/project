from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator (Boss)'),
        ('MANAGER', 'Fleet Manager'),
        ('DISPATCHER', 'Dispatcher'),
        ('SAFETY', 'Safety Officer'),
        ('FINANCE', 'Financial Analyst'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='DISPATCHER')
    is_approved = models.BooleanField(default=False)

    @property
    def is_manager(self):
        return self.is_superuser or self.role in ['ADMIN', 'MANAGER']

    @property
    def is_dispatcher(self):
        return self.is_superuser or self.role in ['ADMIN', 'MANAGER', 'DISPATCHER']

    @property
    def is_safety(self):
        return self.is_superuser or self.role in ['ADMIN', 'MANAGER', 'SAFETY']

    @property
    def is_finance(self):
        return self.is_superuser or self.role in ['ADMIN', 'MANAGER', 'FINANCE']

    @property
    def is_admin(self):
        return self.is_superuser or self.role == 'ADMIN'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
