from django.db import models
from django.core.exceptions import ValidationError
from vehicles.models import Vehicle
from drivers.models import Driver
from accounts.models import CustomUser


class Trip(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='trips')
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT, related_name='trips')
    origin = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    distance_km = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    estimated_duration_mins = models.IntegerField(default=0)
    cargo_weight_kg = models.DecimalField(max_digits=8, decimal_places=2)
    estimated_fuel_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    dispatched_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name='dispatched_trips'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    FUEL_RATE = 0.12  # cost per km (constant)

    def clean(self):
        if self.vehicle and self.cargo_weight_kg:
            if self.cargo_weight_kg > self.vehicle.capacity_kg:
                raise ValidationError(
                    f'Cargo weight ({self.cargo_weight_kg} kg) exceeds vehicle capacity '
                    f'({self.vehicle.capacity_kg} kg). Too heavy!'
                )
        if self.vehicle and self.vehicle.status == 'IN_SHOP':
            raise ValidationError('Selected vehicle is currently In Shop and cannot be assigned.')
        if self.driver and self.driver.duty_status == 'SUSPENDED':
            raise ValidationError('Selected driver is suspended and cannot be assigned.')
        if self.driver and not self.driver.is_license_valid:
            raise ValidationError('Selected driver has an expired license.')

    def save(self, *args, **kwargs):
        if self.distance_km:
            self.estimated_fuel_cost = float(self.distance_km) * self.FUEL_RATE
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Trip #{self.pk}: {self.origin} → {self.destination} [{self.status}]"

    class Meta:
        ordering = ['-created_at']
