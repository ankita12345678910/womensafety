from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection

class Command(BaseCommand):
    help = 'Seeds the database with an admin user.'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        email = 'admin@gmail.com'
        password = 'admin123'

        if not User.objects.filter(username=email).exists():
            user = User.objects.create_superuser(
                username=email,
                email=email,
                password=password,
                first_name='Admin',
                last_name='User'
            )

            # Add custom fields: role, phone_number, address
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE auth_user SET role = %s, phone_number = %s, address = %s WHERE id = %s
            """, ['admin', '1234567890', 'Admin HQ', user.id])

            self.stdout.write(self.style.SUCCESS(f"✅ Admin user created: {email} / {password}"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️ Admin user already exists: {email}"))
