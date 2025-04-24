from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from usersapp.models import UserDetails  # Import your UserDetails model

class Command(BaseCommand):
    help = 'Seeds the database with an admin user.'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        email = 'admin@gmail.com'
        password = 'admin123'

        if not User.objects.filter(username=email).exists():
            # 1. Create the admin user
            user = User.objects.create_superuser(
                username=email,
                email=email,
                password=password,
                first_name='Admin',
                last_name='User'
            )

            # 2. Create related UserDetails record
            UserDetails.objects.create(
                user=user,
                role='admin',
                phone_number='1234567890',
                address='Admin HQ'
            )

            self.stdout.write(self.style.SUCCESS(f"✅ Admin user created: {email} / {password}"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️ Admin user already exists: {email}"))
