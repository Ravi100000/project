from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib import messages
from accounts.decorators import role_required
from .models import Driver


class DriverListView(LoginRequiredMixin, ListView):
    model = Driver
    template_name = 'drivers/list.html'
    context_object_name = 'drivers'
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset().select_related('user')
        q = self.request.GET.get('q', '')
        status = self.request.GET.get('status', '')
        sort = self.request.GET.get('sort', 'user__username')
        if q:
            qs = (
                qs.filter(user__username__icontains=q) |
                qs.filter(license_number__icontains=q) |
                qs.filter(user__first_name__icontains=q) |
                qs.filter(user__last_name__icontains=q)
            )
        if status:
            qs = qs.filter(duty_status=status)
        allowed = {'user__username', '-safety_score', 'safety_score', 'license_expiry', '-license_expiry', '-created_at'}
        if sort in allowed:
            qs = qs.order_by(sort)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['duty_choices'] = Driver.DUTY_STATUS_CHOICES
        ctx['q'] = self.request.GET.get('q', '')
        ctx['selected_status'] = self.request.GET.get('status', '')
        ctx['selected_sort'] = self.request.GET.get('sort', '')
        ctx['selected_group'] = self.request.GET.get('group', '')
        return ctx


@method_decorator(role_required('MANAGER', 'SAFETY'), name='dispatch')
class DriverCreateView(LoginRequiredMixin, CreateView):
    model = Driver
    template_name = 'drivers/form.html'
    fields = ['user', 'license_number', 'license_expiry', 'phone', 'safety_score', 'duty_status']
    success_url = reverse_lazy('driver-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            if hasattr(field.widget, 'attrs'):
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'
        if 'duty_status' in form.fields:
            form.fields['duty_status'].widget.attrs['class'] = 'form-select'
        if 'user' in form.fields:
            form.fields['user'].widget.attrs['class'] = 'form-select'
        if 'license_expiry' in form.fields:
            form.fields['license_expiry'].widget.attrs['type'] = 'date'
        return form

    def form_valid(self, form):
        messages.success(self.request, 'Driver added successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Add Driver'
        return ctx


@method_decorator(role_required('MANAGER', 'SAFETY'), name='dispatch')
class DriverUpdateView(LoginRequiredMixin, UpdateView):
    model = Driver
    template_name = 'drivers/form.html'
    fields = ['license_number', 'license_expiry', 'phone', 'safety_score', 'duty_status']
    success_url = reverse_lazy('driver-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            if hasattr(field.widget, 'attrs'):
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'
        if 'duty_status' in form.fields:
            form.fields['duty_status'].widget.attrs['class'] = 'form-select'
        if 'license_expiry' in form.fields:
            form.fields['license_expiry'].widget.attrs['type'] = 'date'
        return form

    def form_valid(self, form):
        messages.success(self.request, 'Driver updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Edit Driver'
        return ctx


@method_decorator(role_required('MANAGER', 'SAFETY'), name='dispatch')
class DriverDeleteView(LoginRequiredMixin, DeleteView):
    model = Driver
    template_name = 'drivers/confirm_delete.html'
    success_url = reverse_lazy('driver-list')
