from usersapp.models import OwnerRequests, UserDetails
from camerasapp.models import Camera
from django.shortcuts import render, redirect
from django.http import HttpResponse
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import uuid
from .models import OwnerRequests
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
# Create your views here.


class RoleBasedLoginView(LoginView):
    template_name = 'auth/login.html'

    def get_success_url(self):
        role = self.request.user.details.role
        if role == 'admin':
            return reverse_lazy('admin_dashboard')
        elif role == 'owner':
            return reverse_lazy('owner_dashboard')
        elif role == 'viewer':
            return reverse_lazy('viewer_dashboard')


@login_required
def adminDashboard(request):
    return render(request, 'users/admin_dashboard.html')


@login_required
def ownerDashboard(request):
    return render(request, 'users/owner_dashboard.html')


@login_required
def viewerDashboard(request):
    return render(request, 'users/viewer_dashboard.html')


def manageUser(request, id=None):
    is_edit = id and int(id) != -1
    modal_mode = request.GET.get('modal') == '1'

    user = None
    user_details = None
    if is_edit:
        user = get_object_or_404(User, id=id)
        user_details = getattr(user, 'details', None)

    if request.method == 'POST':
        camera_id = request.POST.get('camera_id')
        email = request.POST.get('email')
        fname = request.POST.get('first_name')
        lname = request.POST.get('last_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        role = request.POST.get('role') if not modal_mode else 'viewer'

        if is_edit:
            user.first_name = fname
            user.last_name = lname
            user.email = email
            user.username = email
            user.save()

            if user_details:
                user_details.phone_number = phone
                user_details.address = address
                if not modal_mode:
                    user_details.role = role
                user_details.save()
            else:
                UserDetails.objects.create(
                    user=user,
                    phone_number=phone,
                    address=address,
                    role=role
                )

            return JsonResponse({
                'message': 'User updated successfully.',
                'redirect_url': None if modal_mode else reverse('list_users')
            })

        else:
            # Create new user
            user = User.objects.create_user(
                username=email,
                email=email,
                password=phone,
                first_name=fname,
                last_name=lname
            )

            UserDetails.objects.create(
                user=user,
                phone_number=phone,
                address=address,
                role=role
            )
            if camera_id:
                try:
                    camera = Camera.objects.get(id=camera_id)
                    camera.viewers.add(user)
                except Camera.DoesNotExist:
                    pass

            return JsonResponse({
                'message': 'Viewer added successfully.',
                'redirect_url': None if modal_mode else reverse('list_users')
            })

    # GET (initial load of form)
    button_text = "Update" if is_edit else "Add"

    if modal_mode:
        return render(request, "users/manage_user_form_inner.html", {
            'target_user': user,
            'button_text': button_text,
            'modal_mode': modal_mode
        })

    return render(request, "users/manage_user.html", {
        'target_user': user,
        'target_user_details': user_details,
        'button_text': button_text,
        'modal_mode': modal_mode
    })


def homePage(request):
    return render(request, 'home/index.html')


def requestOwner(request):
    if request.method == "POST":
        email_id = request.POST.get('email')

        # Check if email already exists in OwnerRequests
        if OwnerRequests.objects.filter(email=email_id).exists():
            messages.error(
                request, 'This email is already used, try with another email!')
            return redirect('owner_request')

        # Check if email already exists as a User
        if User.objects.filter(username=email_id).exists():
            messages.error(
                request, 'This email is already used, try with another email!')
            return redirect('owner_request')

        # Process request
        fname = request.POST.get('first_name')
        lname = request.POST.get('last_name')
        phone = request.POST.get('phone')
        business = request.POST.get('business_details')
        address = request.POST.get('address')
        invoice_file = request.FILES.get('invoice')

        invoice_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
        custom_filename = str(int(uuid.uuid4().hex[:5], 16) % 100000).zfill(
            5) + "-" + invoice_file.name
        file_path = os.path.join(invoice_dir, custom_filename)

        fs = FileSystemStorage(location=invoice_dir)
        filename = fs.save(custom_filename, invoice_file)

        if os.path.exists(file_path):
            owner_request = OwnerRequests.objects.create(
                first_name=fname,
                last_name=lname,
                email=email_id,
                phone=phone,
                business_details=business,
                address=address,
                invoice=filename
            )
            messages.success(
                request, 'Your request has been submitted successfully!')
        else:
            messages.error(
                request, 'Failed to upload the invoice. Please try again.')

        return redirect('owner_request')

    return render(request, 'users/owner_request.html')


def listOwnerRequest(request):
    all_requests = OwnerRequests.objects.all()
    return render(request, "users/list_owner_request.html", {
        'all_requests': all_requests
    })


def getOwnerDetailsByAjax(request, id):
    try:
        owner = OwnerRequests.objects.get(id=id)
        html = render(request, 'partials/owner_modal_content.html',
                      {'owner': owner}).content.decode('utf-8')
        return JsonResponse({'html': html, 'current_status': owner.status})
    except OwnerRequests.DoesNotExist:
        return JsonResponse({'html': '<p class="text-danger">Owner not found.</p>'})


def updateOwnerStatus(request, id, status):
    try:
        owner = OwnerRequests.objects.get(id=id)

        if status == 'approved':
            # 1. Create User
            user = User.objects.create_user(
                username=owner.email,
                email=owner.email,
                password='1234',
                first_name=owner.first_name,
                last_name=owner.last_name,
            )

            # 2. Create UserDetails
            UserDetails.objects.create(
                user=user,
                role='owner',
                phone_number=owner.phone,
                address=owner.address,
            )

            owner.delete()
            # 3. (Optional) Send Mail - Uncomment if needed
            '''
            subject = "Your Owner Account Has Been Approved"
            message = f"""
            Hello {owner.first_name},

            Your request to become an Owner has been approved!

            Username: {owner.email}
            Temporary Password: 1234

            Please login using this link:  
            🔗 http://127.0.0.1:8000/login/

            After login, make sure to change your password from your dashboard.

            Best regards,  
            Women Safety Team
            """
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [owner.email],
                fail_silently=False,
            )
             '''
            # 4. Delete from OwnerRequests

            return JsonResponse({
                'success': True,
                'status': status,
                'message': 'Owner approved and credentials sent!'
            })

        else:
            # Rejected or other status update
            owner.status = status
            owner.save()

            return JsonResponse({
                'success': True,
                'status': status,
                'message': f"Request has been {status} successfully."
            })

    except OwnerRequests.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Owner request not found'}, status=404)


def listUsers(request):
    users = UserDetails.objects.select_related('user').filter(
        role__in=['admin', 'owner'],
        user__is_active=True
    ).order_by('-user__date_joined')

    return render(request, 'users/list_user.html', {'users': users})


def delete_user(request, user_id):
    if request.user.id == user_id:
        return JsonResponse({'error': 'Cannot delete yourself.'}, status=400)

    user = get_object_or_404(User, pk=user_id)
    user.is_active = False
    user.save()
    return JsonResponse({'success': True})
