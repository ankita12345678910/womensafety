from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.template.loader import render_to_string
from .models import Camera
from django.views.decorators.http import require_POST


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

    if new_status in ['active', 'inactive', 'deleted']:
        camera.status = new_status
        camera.save()

    # After updating the status, redirect to the camera list
    return redirect('list_cameras')
