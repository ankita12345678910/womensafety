from django.shortcuts import render
from threatsapp.models import ThreatDetection  
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from django.contrib import messages

def manageThreats(request):
    """ Fetch all threats from the database and display them in the template """
    threats = ThreatDetection.objects.all().order_by('-detected_at')  # Fetch all threats, newest first
    return render(request, "threats/manage_threats.html", {"threats": threats})


@csrf_exempt
@login_required
def ajax_review_threat(request):
    if request.method == 'POST':
        threat_id = request.POST.get('threat_id')
        decision = request.POST.get('review_decision')
        try:
            threat = ThreatDetection.objects.get(id=threat_id)
            threat.review_decision = decision
            threat.reviewed_by = request.user
            threat.reviewed_at = timezone.now()
            threat.save()
            return JsonResponse({'status': 'ok'})
        except ThreatDetection.DoesNotExist:
            return JsonResponse({'status': 'error', 'msg': 'Not found'}, status=404)
    return JsonResponse({'status': 'error', 'msg': 'Invalid'}, status=400)

# views.py


@require_POST
def submit_review(request):
    threat_id = request.POST.get('threat_id')
    decision = request.POST.get('review_decision')

    if threat_id and decision:
        try:
            threat = ThreatDetection.objects.get(id=threat_id)
            threat.review_decision = decision 
            if decision == "real":
                threat.status = "verified"
            elif decision == "false":
                threat.status = "false alarm"
            else:
                threat.status = "pending"  # Or leave unchanged
            threat.reviewed_by = request.user
            threat.reviewed_at = timezone.now()
            threat.save()
            messages.success(request, "Review submitted successfully.")
        except ThreatDetection.DoesNotExist:
            messages.error(request, "Threat not found.")
    else:
        messages.error(request, "Missing review data.")

    return redirect('viewer_dashboard')

@login_required
def check_new_alerts(request):
    user = request.user
    # Get all cameras this user is a viewer of
    assigned_cameras = user.viewable_cameras.all()  # from Camera.viewers

    # Get the most recent alert from one of the user's cameras
    latest_threat = ThreatDetection.objects.filter(
        camera__in=assigned_cameras,
        status='pending',
        alert_triggered=True
    ).order_by('-detected_at').first()

    if latest_threat:
        return JsonResponse({
            'alert': True,
            'camera': latest_threat.camera.name,
            'time': latest_threat.detected_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return JsonResponse({'alert': False})