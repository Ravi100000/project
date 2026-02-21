from django.db import models
from vehicles.models import Vehicle


class Maintenance(models.Model):
    EVENT_TYPE_CHOICES = [
        ('OIL_CHANGE', 'Oil Change'),
        ('REPAIR', 'Repair'),
        ('TYRE', 'Tyre Change'),
        ('INSPECTION', 'Inspection'),
        ('BRAKE', 'Brake Service'),
        ('ELECTRICAL', 'Electrical'),
        ('OTHER', 'Other'),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_logs')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    date = models.DateField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    performed_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_event_type_display()} — {self.vehicle.license_plate} ({self.date})"

    class Meta:
        ordering = ['-date']
