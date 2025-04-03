from django.db import models
from django_mysql.models import EnumField
# Create your models here.


class OwnerRequests(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    business_details = models.TextField(null=True, blank=True)
    address = models.TextField(null=True)
    invoice = models.CharField(max_length=150, null=False, blank=False)
    status = EnumField(choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'owner_requests'

    def __str__(self):
        return f"Name: {self.first_name} {self.last_name}, Email: {self.email}, Phone: {self.phone}, Status: {self.status}"
