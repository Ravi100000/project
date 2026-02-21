from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, Q
from .models import Expense


class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'expenses/list.html'
    context_object_name = 'expenses'
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset().select_related('driver__user', 'trip')
        q = self.request.GET.get('q', '')
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')
        sort = self.request.GET.get('sort', '-date')
        if q:
            qs = qs.filter(
                Q(driver__user__username__icontains=q) |
                Q(driver__user__first_name__icontains=q) |
                Q(notes__icontains=q)
            )
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        allowed = {'-date', 'date', '-fuel_cost', 'fuel_cost', '-misc_expense', '-fuel_litres'}
        if sort in allowed:
            qs = qs.order_by(sort)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_fuel'] = Expense.objects.aggregate(s=Sum('fuel_cost'))['s'] or 0
        ctx['total_misc'] = Expense.objects.aggregate(s=Sum('misc_expense'))['s'] or 0
        ctx['total_amount'] = float(ctx['total_fuel']) + float(ctx['total_misc'])
        ctx['q'] = self.request.GET.get('q', '')
        ctx['date_from'] = self.request.GET.get('date_from', '')
        ctx['date_to'] = self.request.GET.get('date_to', '')
        ctx['selected_sort'] = self.request.GET.get('sort', '')
        ctx['selected_group'] = self.request.GET.get('group', '')
        return ctx


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    template_name = 'expenses/form.html'
    fields = ['trip', 'driver', 'date', 'fuel_litres', 'fuel_cost', 'misc_expense', 'notes']
    success_url = reverse_lazy('expense-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for name, field in form.fields.items():
            if name in ('trip', 'driver'):
                field.widget.attrs['class'] = 'form-select'
            elif name == 'notes':
                field.widget.attrs.update({'class': 'form-control', 'rows': 3})
            else:
                field.widget.attrs['class'] = 'form-control'
            if name == 'date':
                field.widget.attrs['type'] = 'date'
        return form

    def form_valid(self, form):
        messages.success(self.request, 'Expense logged successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Log Expense'
        return ctx
