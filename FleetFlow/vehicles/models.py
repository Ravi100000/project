from django.db import models


class Vehicle(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ('VAN', 'Van'),
        ('TRUCK', 'Truck'),
        ('MINI', 'Mini'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('IN_SHOP', 'In Shop'),
        ('IDLE', 'Idle'),
    ]

    license_plate = models.CharField(max_length=20, unique=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPE_CHOICES, default='VAN')
    capacity_kg = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='IDLE')
    odometer = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.license_plate = self.license_plate.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.license_plate} — {self.make} {self.model} ({self.year})"

    class Meta:
        ordering = ['-created_at']
