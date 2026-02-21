from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Maintenance


@receiver(post_save, sender=Maintenance)
def update_vehicle_status_on_repair(sender, instance, created, **kwargs):
    """Automatically set vehicle status to 'In Shop' when a Repair event is logged."""
    if created and instance.event_type == 'REPAIR':
        instance.vehicle.status = 'IN_SHOP'
        instance.vehicle.save(update_fields=['status'])
