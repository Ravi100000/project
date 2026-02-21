import os
import django
import traceback
from django.test import Client
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleetflow.settings')
django.setup()

def test_login():
    client = Client()
    try:
        print("Attempting dispatcher login...")
        response = client.post(reverse('login'), {'username': 'dispatcher1', 'password': 'pass1234'}, follow=True)
        if response.status_code == 200:
            print("Login successful (rendered).")
        else:
            print(f"Login failed with status {response.status_code}")
    except Exception:
        print("\n--- FULL TRACEBACK ---")
        traceback.print_exc()
        print("----------------------\n")

if __name__ == "__main__":
    test_login()
