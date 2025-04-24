from django.db import models
from django.contrib.auth.models import User
from django_mysql.models import EnumField
# Create your models here.

class Camera(models.Model):
    owner=models.ForeignKey(User,on_delete=models.CASCADE,related_name='cameras')
    name = models.CharField(max_length=255)
    ip_address = models.CharField(max_length=100,unique=True)
    status=EnumField(choices=[('active','Active'),('inactive','Inactive'),('deleted','Deleted')],default="active")
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    viewers=models.ManyToManyField(User,related_name="viewable_cameras")
    location=models.TextField(null=True)
    
    class Meta:
        db_table = "cameras"

    def __str__(self):
        return self.ip_address