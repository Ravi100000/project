from django import forms
from django.utils import timezone
from .models import Driver
from accounts.models import CustomUser


class DriverForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )

    class Meta:
        model = Driver
        fields = ['license_number', 'license_expiry', 'phone', 'safety_score', 'duty_status']
        widgets = {
            'license_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'License Number'}),
            'license_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 XXXXX XXXXX'}),
            'safety_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'duty_status': forms.Select(attrs={'class': 'form-select'}),
        }
