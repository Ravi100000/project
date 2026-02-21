from django.db import models
from django.utils import timezone
from accounts.models import CustomUser


class Driver(models.Model):
    DUTY_STATUS_CHOICES = [
        ('ON_DUTY', 'On Duty'),
        ('BREAK', 'On Break'),
        ('SUSPENDED', 'Suspended'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='driver_profile')
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry = models.DateField()
    phone = models.CharField(max_length=20)
    safety_score = models.IntegerField(default=100)
    duty_status = models.CharField(max_length=15, choices=DUTY_STATUS_CHOICES, default='ON_DUTY')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_license_valid(self):
        return self.license_expiry >= timezone.now().date()

    @property
    def safety_badge_color(self):
        if self.safety_score >= 80:
            return 'success'
        elif self.safety_score >= 50:
            return 'warning'
        return 'danger'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.license_number})"

    class Meta:
        ordering = ['user__username']
