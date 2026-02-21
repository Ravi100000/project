import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from django.utils import timezone
from vehicles.models import Vehicle
from drivers.models import Driver
from trips.models import Trip
from maintenance.models import Maintenance
from expenses.models import Expense
from accounts.decorators import role_required


@login_required
@role_required('MANAGER', 'FINANCE')
def analytics_view(request):
    # KPI totals
    total_fuel = Expense.objects.aggregate(s=Sum('fuel_cost'))['s'] or 0
    total_misc = Expense.objects.aggregate(s=Sum('misc_expense'))['s'] or 0
    total_maintenance = Maintenance.objects.aggregate(s=Sum('cost'))['s'] or 0
    total_expenses = float(total_fuel) + float(total_misc) + float(total_maintenance)
    total_vehicles = Vehicle.objects.count()
    active_vehicles = Vehicle.objects.filter(status='ACTIVE').count()
    utilisation_rate = round((active_vehicles / total_vehicles * 100) if total_vehicles else 0, 1)

    # Fuel efficiency trend — monthly fuel cost
    monthly_fuel = (
        Expense.objects.annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('fuel_cost'))
        .order_by('month')
    )
    fuel_labels = [entry['month'].strftime('%b %Y') if entry['month'] else '' for entry in monthly_fuel]
    fuel_data = [float(entry['total']) for entry in monthly_fuel]

    # Top 5 costliest vehicles
    top_vehicles = (
        Expense.objects.filter(trip__isnull=False)
        .values('trip__vehicle__license_plate')
        .annotate(total=Sum('fuel_cost'))
        .order_by('-total')[:5]
    )
    vehicle_labels = [v['trip__vehicle__license_plate'] or 'Unknown' for v in top_vehicles]
    vehicle_data = [float(v['total']) for v in top_vehicles]

    # Dead stock vehicles — no trips in last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    active_vehicle_ids = Trip.objects.filter(
        created_at__gte=thirty_days_ago
    ).values_list('vehicle_id', flat=True).distinct()
    dead_stock = Vehicle.objects.exclude(id__in=active_vehicle_ids)

    # Monthly summary (last 6 months)
    monthly_maintenance = (
        Maintenance.objects.annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('cost'))
        .order_by('month')
    )

    context = {
        'total_fuel': total_fuel,
        'total_misc': total_misc,
        'total_maintenance': total_maintenance,
        'total_expenses': total_expenses,
        'utilisation_rate': utilisation_rate,
        'fuel_labels': json.dumps(fuel_labels),
        'fuel_data': json.dumps(fuel_data),
        'vehicle_labels': json.dumps(vehicle_labels),
        'vehicle_data': json.dumps(vehicle_data),
        'dead_stock': dead_stock,
        'monthly_maintenance': monthly_maintenance,
    }
    return render(request, 'analytics/analytics.html', context)
