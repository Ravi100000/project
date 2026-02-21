from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.decorators import role_required
from .models import Vehicle
from .forms import VehicleForm


class VehicleListView(LoginRequiredMixin, ListView):
    model = Vehicle
    template_name = 'vehicles/list.html'
    context_object_name = 'vehicles'
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '')
        v_type = self.request.GET.get('type', '')
        status = self.request.GET.get('status', '')
        sort = self.request.GET.get('sort', '-created_at')
        if q:
            qs = qs.filter(license_plate__icontains=q) | qs.filter(make__icontains=q) | qs.filter(model__icontains=q)
        if v_type:
            qs = qs.filter(vehicle_type=v_type)
        if status:
            qs = qs.filter(status=status)
        # Allow only safe sort fields
        allowed = {
            '-created_at', 'created_at', 'license_plate', 'make', 'odometer', '-odometer', 'year', '-year'
        }
        if sort in allowed:
            qs = qs.order_by(sort)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['vehicle_types'] = Vehicle.VEHICLE_TYPE_CHOICES
        ctx['status_choices'] = Vehicle.STATUS_CHOICES
        ctx['q'] = self.request.GET.get('q', '')
        ctx['selected_type'] = self.request.GET.get('type', '')
        ctx['selected_status'] = self.request.GET.get('status', '')
        ctx['selected_sort'] = self.request.GET.get('sort', '')
        ctx['selected_group'] = self.request.GET.get('group', '')
        return ctx


@method_decorator(role_required('MANAGER'), name='dispatch')
class VehicleCreateView(LoginRequiredMixin, CreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'vehicles/form.html'
    success_url = reverse_lazy('vehicle-list')

    def form_valid(self, form):
        messages.success(self.request, 'Vehicle added successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Add New Vehicle'
        return ctx


@method_decorator(role_required('MANAGER'), name='dispatch')
class VehicleUpdateView(LoginRequiredMixin, UpdateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'vehicles/form.html'
    success_url = reverse_lazy('vehicle-list')

    def form_valid(self, form):
        messages.success(self.request, 'Vehicle updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Edit Vehicle'
        return ctx


@method_decorator(role_required('MANAGER'), name='dispatch')
class VehicleDeleteView(LoginRequiredMixin, DeleteView):
    model = Vehicle
    template_name = 'vehicles/confirm_delete.html'
    success_url = reverse_lazy('vehicle-list')

    def form_valid(self, form):
        messages.success(self.request, 'Vehicle deleted successfully!')
        return super().form_valid(form)
