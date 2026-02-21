from django.db import models
from trips.models import Trip
from drivers.models import Driver


class Expense(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='expenses')
    date = models.DateField()
    fuel_litres = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fuel_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    misc_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_cost(self):
        return self.fuel_cost + self.misc_expense

    def __str__(self):
        return f"Expense #{self.pk} — {self.driver} ({self.date})"

    class Meta:
        ordering = ['-date']
