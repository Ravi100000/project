from django.contrib.auth import authenticate
from accounts.models import CustomUser
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleetflow.settings')
django.setup()

users = [
    ('admin', 'admin123'),
    ('dispatcher1', 'pass1234'),
    ('safety1', 'pass1234'),
    ('finance1', 'pass1234')
]

for u, p in users:
    user = authenticate(username=u, password=p)
    if user:
        print(f"{u}: OK ({user.role})")
    else:
        existing = CustomUser.objects.filter(username=u).first()
        if existing:
            print(f"{u}: WRONG PASSWORD (Role: {existing.role})")
        else:
            print(f"{u}: NOT FOUND")
