from django.shortcuts import render
from threatsapp.models import ThreatDetection  # Ensure your model is correctly imported

def manageThreats(request):
    """ Fetch all threats from the database and display them in the template """
    threats = ThreatDetection.objects.all().order_by('-detected_at')  # Fetch all threats, newest first
    return render(request, "threats/manage_threats.html", {"threats": threats})