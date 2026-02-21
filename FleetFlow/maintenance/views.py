from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib import messages
from accounts.decorators import role_required
from .models import Maintenance
from vehicles.models import Vehicle


class MaintenanceListView(LoginRequiredMixin, ListView):
    model = Maintenance
    template_name = 'maintenance/list.html'
    context_object_name = 'records'
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset().select_related('vehicle')
        q = self.request.GET.get('q', '')
        event_type = self.request.GET.get('event_type', '')
        vehicle_id = self.request.GET.get('vehicle', '')
        sort = self.request.GET.get('sort', '-date')
        if q:
            qs = (
                qs.filter(vehicle__license_plate__icontains=q) |
                qs.filter(description__icontains=q) |
                qs.filter(performed_by__icontains=q)
            )
        if event_type:
            qs = qs.filter(event_type=event_type)
        if vehicle_id:
            qs = qs.filter(vehicle_id=vehicle_id)
        allowed = {'-date', 'date', '-cost', 'cost'}
        if sort in allowed:
            qs = qs.order_by(sort)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['vehicles'] = Vehicle.objects.all().order_by('license_plate')
        ctx['q'] = self.request.GET.get('q', '')
        ctx['selected_event'] = self.request.GET.get('event_type', '')
        ctx['selected_vehicle'] = self.request.GET.get('vehicle', '')
        ctx['selected_sort'] = self.request.GET.get('sort', '')
        ctx['selected_group'] = self.request.GET.get('group', '')
        return ctx


@method_decorator(role_required('MANAGER'), name='dispatch')
class MaintenanceCreateView(LoginRequiredMixin, CreateView):
    model = Maintenance
    template_name = 'maintenance/form.html'
    fields = ['vehicle', 'event_type', 'date', 'cost', 'performed_by', 'description']
    success_url = reverse_lazy('maintenance-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for name, field in form.fields.items():
            if name in ('vehicle', 'event_type'):
                field.widget.attrs['class'] = 'form-select'
            elif name == 'description':
                field.widget.attrs.update({'class': 'form-control', 'rows': 3})
            else:
                field.widget.attrs['class'] = 'form-control'
            if name == 'date':
                field.widget.attrs['type'] = 'date'
        return form

    def form_valid(self, form):
        messages.success(self.request, 'Maintenance record saved!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Log Maintenance Event'
        return ctx
