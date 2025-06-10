from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.template.loader import render_to_string
from .models import Camera
from django.views.decorators.http import require_POST
from django.conf import settings
import os
import subprocess


@login_required(login_url='login')
def manageCamera(request, id=None):
    # Check if it's an edit (id is provided)
    is_edit = id is not None and int(id) != -1
    camera = get_object_or_404(
        Camera, id=id, owner=request.user) if is_edit else None

    if request.method == 'POST':
        name = request.POST.get('name')
        ip_address = request.POST.get('ip_address')
        location = request.POST.get('location')

        if is_edit:
            # Update existing camera
            camera.name = name
            camera.ip_address = ip_address
            camera.location = location
            camera.save()

            return JsonResponse({
                'message': 'Camera updated successfully.',
                'redirect_url': None  # Adjust this URL as needed
            })

        else:
            # Create new camera
            Camera.objects.create(
                owner=request.user,
                name=name,
                ip_address=ip_address,
                location=location
            )

            # Optionally render the form after creating a new camera
            html = render_to_string("cameras/manage_camera_form_inner.html", {
                'camera': None,  # no camera since it's a new one
                'button_text': 'Add'
            }, request=request)

            return JsonResponse({
                'message': 'Camera added successfully.',
                'html': html  # Return the updated form for re-rendering
            })

    # If GET request: show the form
    button_text = "Update" if is_edit else "Add"

    # Render the form
    return render(request, "cameras/manage_camera.html", {
        'camera': camera,
        'button_text': button_text
    })


@login_required(login_url='login')
def listCameras(request):
    active_cameras = Camera.objects.filter(status='active')
    inactive_cameras = Camera.objects.filter(status='inactive')

    context = {
        'active_cameras': active_cameras,
        'inactive_cameras': inactive_cameras,
    }

    return render(request, 'cameras/list_cameras.html', context)


@require_POST
def change_camera_status(request, camera_id):
    camera = get_object_or_404(Camera, id=camera_id)
    new_status = request.POST.get('status')

    camera.status = new_status
    camera.save()

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pid_dir = os.path.join(BASE_DIR, 'pids')
    os.makedirs(pid_dir, exist_ok=True)

    pid_file = os.path.join(pid_dir, f'camera_{camera_id}.pid')

    if new_status == 'active':
        python_path = r"C:\demo\Weapons-and-Knives-Detector-with-YOLOv8\myenv\Scripts\python.exe"
        script_path = r"C:\demo\Weapons-and-Knives-Detector-with-YOLOv8\detecting-images.py"
        log_path = rf"C:\demo\Weapons-and-Knives-Detector-with-YOLOv8\logs\camera_{camera_id}.log"
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        process = subprocess.Popen(
            [python_path, script_path, '--camera_id', str(camera_id)],
            stdout=open(log_path, 'a'),
            stderr=subprocess.STDOUT,
        )

        with open(pid_file, 'w') as f:
            f.write(str(process.pid))

    elif new_status == 'inactive':
        if os.path.exists(pid_file):
            try:
                with open(pid_file, 'r') as f:
                    pid = int(f.read())
                subprocess.call(['taskkill', '/F', '/PID', str(pid)])
                os.remove(pid_file)
            except Exception as e:
                print(f"Error stopping camera process: {e}")

    return redirect('list_cameras')


def monitor_camera(request, camera_id):
    camera = get_object_or_404(Camera, id=camera_id)
    return render(request, 'cameras/monitor_camera.html', {'camera': camera})


@login_required
def view_all_cameras(request):
    user = request.user
    active_cameras = user.viewable_cameras.filter(status='active')
    return render(request, 'cameras/view_all_cameras.html', {'active_cameras': active_cameras})