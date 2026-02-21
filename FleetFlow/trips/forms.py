from django import forms
from vehicles.models import Vehicle
from drivers.models import Driver
from .models import Trip
from django.utils import timezone


class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['vehicle', 'driver', 'origin', 'destination', 'cargo_weight_kg', 'notes']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'driver': forms.Select(attrs={'class': 'form-select'}),
            'origin': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Destination City'}),
            'cargo_weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        is_update = kwargs.pop('is_update', False)
        super().__init__(*args, **kwargs)
        if not is_update:
            self.initial['origin'] = 'Ahmedabad'
        today = timezone.now().date()
        if is_update:
            # For updates: show all non-in_shop vehicles (keeps current vehicle visible)
            self.fields['vehicle'].queryset = Vehicle.objects.exclude(status='IN_SHOP')
            # Show non-suspended drivers with valid license
            self.fields['driver'].queryset = Driver.objects.exclude(
                duty_status='SUSPENDED'
            ).filter(license_expiry__gte=today).select_related('user')
        else:
            # For new trips: only ACTIVE vehicles
            self.fields['vehicle'].queryset = Vehicle.objects.filter(status='ACTIVE')
            # Only ON_DUTY drivers with valid license
            self.fields['driver'].queryset = Driver.objects.filter(
                duty_status='ON_DUTY',
                license_expiry__gte=today
            ).select_related('user')
