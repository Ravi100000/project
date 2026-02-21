from django import forms
from .models import Vehicle


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['license_plate', 'make', 'model', 'year', 'vehicle_type', 'capacity_kg', 'odometer', 'status']
        widgets = {
            'license_plate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., KA01AB1234'}),
            'make': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Toyota'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Hiace'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1990, 'max': 2030}),
            'vehicle_type': forms.Select(attrs={'class': 'form-select'}),
            'capacity_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'odometer': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
