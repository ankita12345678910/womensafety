from django.db import migrations, connection

def add_fields_to_auth_user(apps, schema_editor):
    with connection.cursor() as cursor:
        # Add ENUM role column if it doesn't exist
        cursor.execute("""
            ALTER TABLE auth_user ADD COLUMN role ENUM('admin', 'owner', 'viewer') DEFAULT 'viewer';
        """)
        
        # Add phone_number column
        cursor.execute("""
            ALTER TABLE auth_user ADD COLUMN phone_number VARCHAR(20) NULL;
        """)

        # Add address column
        cursor.execute("""
            ALTER TABLE auth_user ADD COLUMN address TEXT NULL;
        """)

        # Add updated_at column
        cursor.execute("""
            ALTER TABLE auth_user ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;
        """)

def remove_fields_from_auth_user(apps, schema_editor):
    with connection.cursor() as cursor:
        # Drop the added columns
        cursor.execute("ALTER TABLE auth_user DROP COLUMN role;")
        cursor.execute("ALTER TABLE auth_user DROP COLUMN phone_number;")
        cursor.execute("ALTER TABLE auth_user DROP COLUMN address;")
        cursor.execute("ALTER TABLE auth_user DROP COLUMN updated_at;")

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),  # Adjust based on your last auth migration
    ]

    operations = [
        migrations.RunPython(add_fields_to_auth_user, reverse_code=remove_fields_from_auth_user),
    ]
