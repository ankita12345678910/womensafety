from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.template.loader import render_to_string
from .models import Camera

@login_required(login_url='login')
def manageCamera(request, id=None):
    is_edit = id is not None and int(id) != -1
    camera = get_object_or_404(Camera, id=id, owner=request.user) if is_edit else None

    if request.method == 'POST':
        name = request.POST.get('name')
        ip_address = request.POST.get('ip_address')
        location = request.POST.get('location')

        if is_edit:
            # Update camera
            camera.name = name
            camera.ip_address = ip_address
            camera.location = location
            camera.save()

            return JsonResponse({
                'message': 'Camera updated successfully.',
                'redirect_url': None  # Adjust this to your camera list URL
            })

        else:
            # Create new camera
            Camera.objects.create(
                owner=request.user,
                name=name,
                ip_address=ip_address,
                location=location
            )

            html = render_to_string("cameras/manage_camera_form_inner.html", {
                'camera': None,
                'button_text': 'Add'
            }, request=request)

            return JsonResponse({
                'message': 'Camera added successfully.',
                'html': html
            })

    # GET request: show form
    button_text = "Update" if is_edit else "Add"
    return render(request, "cameras/manage_camera.html", {
        'camera': camera,
        'button_text': button_text
    })

