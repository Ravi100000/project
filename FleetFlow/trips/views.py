from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from vehicles.models import Vehicle
from drivers.models import Driver
from .models import Trip
from .forms import TripForm
from .utils import get_route_info
from django import forms as django_forms
from django.db.models import Q


class TripListView(LoginRequiredMixin, ListView):
    model = Trip
    template_name = 'trips/list.html'
    context_object_name = 'trips'
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset().select_related('vehicle', 'driver__user', 'dispatched_by')
        q = self.request.GET.get('q', '')
        status = self.request.GET.get('status', '')
        v_type = self.request.GET.get('type', '')
        sort = self.request.GET.get('sort', '-created_at')

        if q:
            qs = qs.filter(Q(origin__icontains=q) | Q(destination__icontains=q))
        if status:
            qs = qs.filter(status=status)
        if v_type:
            qs = qs.filter(vehicle__vehicle_type=v_type)

        allowed_sorts = {
            '-created_at', 'created_at', 'status', '-distance_km', 'distance_km', '-estimated_fuel_cost'
        }
        if sort in allowed_sorts:
            qs = qs.order_by(sort)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_choices'] = Trip.STATUS_CHOICES
        ctx['vehicle_types'] = Vehicle.VEHICLE_TYPE_CHOICES
        ctx['q'] = self.request.GET.get('q', '')
        ctx['selected_status'] = self.request.GET.get('status', '')
        ctx['selected_type'] = self.request.GET.get('type', '')
        ctx['selected_sort'] = self.request.GET.get('sort', '')
        ctx['selected_group'] = self.request.GET.get('group', '')
        return ctx


class TripDetailView(LoginRequiredMixin, DetailView):
    model = Trip
    template_name = 'trips/detail.html'
    context_object_name = 'trip'


@method_decorator(role_required('MANAGER', 'DISPATCHER'), name='dispatch')
class TripCreateView(LoginRequiredMixin, CreateView):
    model = Trip
    form_class = TripForm
    template_name = 'trips/form.html'
    success_url = reverse_lazy('trip-list')

    def form_valid(self, form):
        destination = form.cleaned_data.get('destination')
        distance, duration = get_route_info(destination)
        
        form.instance.distance_km = distance
        form.instance.estimated_duration_mins = duration
        form.instance.dispatched_by = self.request.user
        
        messages.success(
            self.request, 
            f'Trip dispatched! Calculated distance: {distance}km, Duration: {duration} mins.'
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Dispatch New Trip'
        return ctx


@method_decorator(role_required('MANAGER', 'DISPATCHER'), name='dispatch')
class TripUpdateView(LoginRequiredMixin, UpdateView):
    model = Trip
    form_class = TripForm
    template_name = 'trips/update.html'
    success_url = reverse_lazy('trip-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['is_update'] = True
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Add status field to update form
        form.fields['status'] = django_forms.ChoiceField(
            choices=Trip.STATUS_CHOICES,
            initial=self.object.status,
            widget=django_forms.Select(attrs={'class': 'form-select'})
        )
        return form

    def form_valid(self, form):
        old_trip = Trip.objects.get(pk=self.object.pk)
        new_status = form.cleaned_data.get('status')
        trip = form.save(commit=False)
        trip.status = new_status

        # Handle side effects on status change
        if old_trip.status != new_status:
            if new_status == 'IN_PROGRESS':
                trip.vehicle.status = 'ACTIVE'
                trip.vehicle.save(update_fields=['status'])
                trip.driver.duty_status = 'ON_DUTY'
                trip.driver.save(update_fields=['duty_status'])
            elif new_status == 'COMPLETED':
                if trip.distance_km:
                    trip.vehicle.odometer += trip.distance_km
                    trip.vehicle.save(update_fields=['odometer'])
                trip.vehicle.status = 'IDLE'
                trip.vehicle.save(update_fields=['status'])
                trip.driver.duty_status = 'BREAK'
                trip.driver.save(update_fields=['duty_status'])
            elif new_status == 'CANCELLED':
                trip.vehicle.status = 'IDLE'
                trip.vehicle.save(update_fields=['status'])
                trip.driver.duty_status = 'ON_DUTY'
                trip.driver.save(update_fields=['duty_status'])

        trip.save()
        messages.success(self.request, f'Trip #{trip.pk} updated to {trip.get_status_display()}!')
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Update Trip'
        ctx['trip'] = self.object
        return ctx
