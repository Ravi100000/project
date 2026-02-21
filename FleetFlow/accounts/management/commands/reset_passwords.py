from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import secrets


class Command(BaseCommand):
    help = 'Create test users for all roles with random passwords.'

    def handle(self, *args, **options):
        User = get_user_model()

        # Define India-styled test users: username, first_name, last_name, role, is_superuser, is_staff, password
        test_users = [
            ('ceo_rohit', 'Rohit', 'Kumar', 'ADMIN', True, True, 'Rohit@2026'),
            ('admin_priya', 'Priya', 'Desai', 'ADMIN', False, True, 'Priya@2026'),
            ('manager_arjun', 'Arjun', 'Patel', 'MANAGER', False, True, 'Arjun@2026'),
            ('dispatcher_sneha', 'Sneha', 'Rao', 'DISPATCHER', False, False, 'Sneha@2026'),
            ('safety_kavita', 'Kavita', 'Nair', 'SAFETY', False, False, 'Kavita@2026'),
            ('finance_suresh', 'Suresh', 'Gandhi', 'FINANCE', False, False, 'Suresh@2026'),
        ]

        self.stdout.write('Creating/updating India test users...\n')
        for username, first, last, role, is_super, is_staff, pwd in test_users:
            user, created = User.objects.get_or_create(username=username, defaults={
                'first_name': first,
                'last_name': last,
                'email': f'{username}@fleetflow.in',
                'is_superuser': is_super,
                'is_staff': is_staff,
                'is_approved': True,
            })

            # Update fields if user already existed
            if not created:
                updated = False
                if user.first_name != first:
                    user.first_name = first
                    updated = True
                if user.last_name != last:
                    user.last_name = last
                    updated = True
                if user.email != f'{username}@fleetflow.in':
                    user.email = f'{username}@fleetflow.in'
                    updated = True
                if user.is_staff != is_staff:
                    user.is_staff = is_staff
                    updated = True
                if user.is_superuser != is_super:
                    user.is_superuser = is_super
                    updated = True
                if updated:
                    user.save()

            # Set role and password and ensure approved
            user.role = role
            user.set_password(pwd)
            user.is_approved = True
            user.save()

            action = 'Created' if created else 'Updated'
            self.stdout.write(f"{action}: {username} ({first} {last}) role={role} email={user.email} password={pwd}")

        self.stdout.write(self.style.SUCCESS('\nDone.'))
