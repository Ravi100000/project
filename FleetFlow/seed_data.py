"""
FleetFlow Seed Script — creates superuser + demo data
Run: python manage.py shell < seed_data.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleetflow.settings')
django.setup()

from django.contrib.auth import get_user_model
from vehicles.models import Vehicle
from drivers.models import Driver
from trips.models import Trip
from datetime import date, timedelta

User = get_user_model()

# CREATE SUPERUSER / MANAGER
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@fleetflow.com',
        password='admin123',
        role='MANAGER',
        first_name='Admin',
        last_name='Manager'
    )
    print('✅ Superuser created: admin / admin123')
else:
    admin = User.objects.get(username='admin')
    print('ℹ️  Superuser already exists')

# CREATE ROLE USERS
roles = [
    ('dispatcher1', 'Jane', 'Smith', 'DISPATCHER'),
    ('safety1', 'Bob', 'Brown', 'SAFETY'),
    ('finance1', 'Carol', 'White', 'FINANCE'),
]
for uname, fn, ln, role in roles:
    if not User.objects.filter(username=uname).exists():
        User.objects.create_user(
            username=uname, password='pass1234',
            role=role, first_name=fn, last_name=ln
        )
        print(f'✅ Created {role} user: {uname} / pass1234')

# CREATE VEHICLES
vehicles_data = [
    ('KA01AB1234', 'Toyota', 'Hiace', 2020, 'VAN', 800, 'ACTIVE', 12500),
    ('MH04CD5678', 'Tata', 'Prima', 2019, 'TRUCK', 5000, 'ACTIVE', 89000),
    ('DL09EF9012', 'Mahindra', 'Bolero', 2021, 'MINI', 500, 'IDLE', 4300),
    ('TN11GH3456', 'Ashok Leyland', 'Dost', 2022, 'TRUCK', 3000, 'ACTIVE', 31000),
    ('GJ05IJ7890', 'Toyota', 'Innova', 2023, 'VAN', 600, 'IN_SHOP', 8900),
    # Additional vehicles for broader testing
    ('KA02XY1111', 'Isuzu', 'Elf', 2018, 'TRUCK', 4000, 'ACTIVE', 120000),
    ('WB03LM2222', 'Suzuki', 'Eeco', 2017, 'VAN', 700, 'ACTIVE', 98000),
    ('UP04OP3333', 'Force', 'Traveller', 2016, 'MINI', 600, 'IDLE', 56000),
    ('RJ05QR4444', 'Tata', 'Ace', 2015, 'TRUCK', 1200, 'IN_SHOP', 200000),
]
created_vehicles = []
for plate, make, model, year, vtype, cap, status, odo in vehicles_data:
    v, created = Vehicle.objects.get_or_create(
        license_plate=plate,
        defaults=dict(make=make, model=model, year=year, vehicle_type=vtype,
                      capacity_kg=cap, status=status, odometer=odo)
    )
    created_vehicles.append(v)
    if created:
        print(f'✅ Vehicle: {plate}')

# CREATE DRIVER USERS + DRIVER PROFILES
driver_users = [
    ('driver1', 'Ravi', 'Kumar', 'DL', 'DL-MH-0120230012345', date(2027, 6, 30), '+91 9876543210', 95),
    ('driver2', 'Suresh', 'Rao', 'DL', 'DL-KA-0220240067890', date(2025, 1, 15), '+91 9123456789', 72),
    ('driver3', 'Arjun', 'Nair', 'DL', 'DL-TN-0320220099123', date(2028, 3, 20), '+91 9845671234', 88),
    # Driver with expired license
    ('driver4', 'Manoj', 'Singh', 'DL', 'DL-UP-0520200000123', date.today() - timedelta(days=30), '+91 9012345678', 60),
    # Suspended driver (status updated after creation)
    ('driver5', 'Deepak', 'Patel', 'DL', 'DL-GJ-0620250000456', date(2026, 12, 31), '+91 9988776655', 40),
]
created_drivers = []
for uname, fn, ln, _, lic_num, lic_exp, phone, score in driver_users:
    u, _ = User.objects.get_or_create(
        username=uname,
        defaults=dict(first_name=fn, last_name=ln, role='DISPATCHER', password='pass1234')
    )
    if not u.has_usable_password():
        u.set_password('pass1234')
        u.save()
    d, created = Driver.objects.get_or_create(
        user=u,
        defaults=dict(license_number=lic_num, license_expiry=lic_exp,
                      phone=phone, safety_score=score, duty_status='ON_DUTY')
    )
    created_drivers.append(d)
    if created:
        print(f'✅ Driver: {fn} {ln} ({uname})')
    # Adjust specific test driver statuses
    if uname == 'driver5':
        d.duty_status = 'SUSPENDED'
        d.save()
        print(f'⚠️  Driver suspended for test: {uname}')

# CREATE SAMPLE TRIPS
if created_drivers and created_vehicles:
    active_vehicles = [v for v in created_vehicles if v.status == 'ACTIVE']
    on_duty_drivers = created_drivers[:2]
    trips_data = [
        (active_vehicles[0], on_duty_drivers[0], 'Mumbai', 'Pune', 120, 400),
        (active_vehicles[1], on_duty_drivers[1], 'Bangalore', 'Chennai', 350, 2500),
        (active_vehicles[2] if len(active_vehicles) > 2 else active_vehicles[0],
         on_duty_drivers[0], 'Delhi', 'Jaipur', 280, 1800),
    ]
    for v, d, orig, dest, dist, cargo in trips_data:
        if not Trip.objects.filter(vehicle=v, origin=orig, destination=dest).exists():
            try:
                t = Trip(
                    vehicle=v, driver=d, origin=orig, destination=dest,
                    distance_km=dist, cargo_weight_kg=cargo,
                    dispatched_by=admin, status='PENDING'
                )
                t.full_clean()
                t.save()
                print(f'✅ Trip: {orig} → {dest}')
            except Exception as e:
                print(f'⚠️  Trip skipped ({orig}→{dest}): {e}')

# EXTRA TRIPS TO DEMONSTRATE VALIDATIONS (in-shop vehicle, overweight, expired/suspended drivers)
extra_trips = []
if created_drivers and created_vehicles:
    in_shop = next((v for v in created_vehicles if v.status == 'IN_SHOP'), None)
    heavy_vehicle = next((v for v in created_vehicles if float(v.capacity_kg) >= 4000), None)
    expired_driver = next((d for d in created_drivers if not d.is_license_valid), None)
    suspended_driver = next((d for d in created_drivers if d.duty_status == 'SUSPENDED'), None)

    if in_shop:
        extra_trips.append((in_shop, created_drivers[0], 'TestCityA', 'TestCityB', 50, 100))
    if heavy_vehicle:
        extra_trips.append((heavy_vehicle, created_drivers[0], 'HeavyOrigin', 'HeavyDest', 10, float(heavy_vehicle.capacity_kg) + 1000))
    if expired_driver:
        extra_trips.append((created_vehicles[0], expired_driver, 'ExpiryTown', 'NextTown', 70, 200))
    if suspended_driver:
        extra_trips.append((created_vehicles[1], suspended_driver, 'SuspendVille', 'Nowhere', 30, 100))

    for v, d, orig, dest, dist, cargo in extra_trips:
        try:
            if not Trip.objects.filter(vehicle=v, origin=orig, destination=dest).exists():
                t = Trip(
                    vehicle=v, driver=d, origin=orig, destination=dest,
                    distance_km=dist, cargo_weight_kg=cargo,
                    dispatched_by=admin, status='PENDING'
                )
                t.full_clean()
                t.save()
                print(f'✅ Extra Trip: {orig} → {dest}')
        except Exception as e:
            print(f'⚠️  Extra trip skipped ({orig}→{dest}): {e}')

print('\n✅ Seed complete! Login at http://127.0.0.1:8000/login/')
print('   Admin: admin / admin123')
print('   Dispatcher: dispatcher1 / pass1234')
print('   Safety: safety1 / pass1234')
print('   Finance: finance1 / pass1234')
