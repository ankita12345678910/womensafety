from django.db import models
from django_mysql.models import EnumField
from django.contrib.auth.models import User

# Create your models here.


class ThreatDetection(models.Model):
    camera = models.ForeignKey(
        'camerasapp.Camera', on_delete=models.CASCADE, related_name="threat_detections")
    # Path to detected frame (screenshot)
    image = models.CharField(max_length=255)
    # Nullable field for weapon detection
    weapon_type = models.CharField(max_length=50, null=True, blank=True)
    # AI confidence level (e.g., 85%)
    confidence = models.FloatField(null=True,)
    # Path to recorded audio evidence
    audio = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField()  # Detected latitude
    longitude = models.FloatField()  # Detected longitude
    detected_at = models.DateTimeField(auto_now_add=True)  # Time of detection
    emotion = models.CharField(max_length=50)  # Detected emotion
    gender = models.CharField(max_length=10)  # Detected gender
    status = EnumField(choices=[
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('false alarm', 'False Alarm')
    ], default='pending')  # Verification status
    # TRUE if an alert was sent, FALSE otherwise
    alert_triggered = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='reviewed_threats',
        help_text="Viewer who reviewed the alert"
    )

    review_decision = EnumField(choices=[
        ('real', 'Real'),
        ('false', 'False'),
        ('uncertain', 'Uncertain')
    ], null=True, blank=True)

    escalated = models.BooleanField(default=False)
    escalated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'threat_detections'

    def __str__(self):
        return f"Threat {self.id} detected by Camera {self.camera_id}"
