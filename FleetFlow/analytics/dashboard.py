from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.shortcuts import redirect
from django.conf import settings
from django.db.models import Q
import django.utils.timezone
from vehicles.models import Vehicle
from trips.models import Trip
from drivers.models import Driver
from maintenance.models import Maintenance


@require_GET
@login_required
def dashboard_view(request):
    # Extra safety: ensure unauthenticated users are redirected (double-check)
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL)
    # General Stats (Fleet Manager / Admin)
    total_vehicles = Vehicle.objects.count()
    active_vehicles = Vehicle.objects.filter(status='ACTIVE').count()
    in_shop = Vehicle.objects.filter(status='IN_SHOP').count()
    pending_trips = Trip.objects.filter(status='PENDING').count()
    utilisation = round((active_vehicles / total_vehicles * 100) if total_vehicles else 0, 1)

    # Safety Stats (Safety Officer)
    total_drivers = Driver.objects.count()
    from django.db.models import Avg, Sum
    avg_safety_score = Driver.objects.aggregate(Avg('safety_score'))['safety_score__avg'] or 0
    expired_licenses = Driver.objects.filter(license_expiry__lt=django.utils.timezone.now()).count()

    # Finance Stats (Financial Analyst)
    from expenses.models import Expense
    total_expenses = Expense.objects.aggregate(Sum('fuel_cost'), Sum('misc_expense'))
    total_fuel = total_expenses['fuel_cost__sum'] or 0
    total_misc = total_expenses['misc_expense__sum'] or 0
    grand_total = total_fuel + total_misc

    # Recent trips with filters (Dispatcher)
    trips_qs = Trip.objects.select_related('vehicle', 'driver__user').order_by('-created_at')
    v_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    if v_type:
        trips_qs = trips_qs.filter(vehicle__vehicle_type=v_type)
    if status:
        trips_qs = trips_qs.filter(status=status)
    recent_trips = trips_qs[:10]

    context = {
        'total_vehicles': total_vehicles,
        'active_vehicles': active_vehicles,
        'in_shop': in_shop,
        'pending_trips': pending_trips,
        'utilisation': utilisation,
        'recent_trips': recent_trips,
        'vehicle_types': Vehicle.VEHICLE_TYPE_CHOICES,
        'status_choices': Trip.STATUS_CHOICES,
        'selected_type': v_type,
        'selected_status': status,
        'total_drivers': total_drivers,
        'avg_safety_score': round(avg_safety_score, 1),
        'expired_licenses': expired_licenses,
        'total_fuel': total_fuel,
        'total_misc': total_misc,
        'grand_total': grand_total,
    }
    return render(request, 'dashboard/dashboard.html', context)
