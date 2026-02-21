import os
import django
from django.test import Client
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleetflow.settings')
django.setup()

def test_logins():
    client = Client()
    users = [
        ('admin', 'admin123', '/dashboard/'),
        ('dispatcher1', 'pass1234', '/trips/'),
        ('safety1', 'pass1234', '/drivers/'),
        ('finance1', 'pass1234', '/expenses/'),
    ]

    print("--- Login Verification Test ---")
    for username, password, expected_path in users:
        print(f"Testing {username}...", end=" ")
        # 1. Get login page (to get CSRF token if needed, though Client.login handles it)
        response = client.post(reverse('login'), {'username': username, 'password': password}, follow=True)
        
        # Check if login was successful (usually redirects to dashboard or role-specific page)
        if response.status_code == 200:
            final_path = response.request.get('PATH_INFO')
            if expected_path in final_path:
                print(f"PASS (Landed on {final_path})")
            else:
                print(f"FAIL (Expected {expected_path}, landed on {final_path})")
        else:
            print(f"FAIL (HTTP {response.status_code})")
        
        # Logout for next test
        client.logout()

if __name__ == "__main__":
    test_logins()
