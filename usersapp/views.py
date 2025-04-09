from usersapp.models import OwnerRequests
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

# Create your views here.


@login_required
def adminDashboard(request):
    return render(request, 'users/admin_dashboard.html')


@login_required(login_url='login')
def manageUser(request, id=None):
    is_edit = id and int(id) != -1
    user = None

    if is_edit:
        user = User.objects.raw("SELECT * FROM auth_user WHERE id=%s", [id])[0]

    if request.method == 'POST':
        email = request.POST.get('email')
        fname = request.POST.get('first_name')
        lname = request.POST.get('last_name')
        phone = request.POST.get('phone')
        role = request.POST.get('role')
        address = request.POST.get('address')
        if is_edit:
            user.first_name = fname
            user.last_name = lname
            user.email = email
            user.username = email
            user.save()

            cursor = connection.cursor()
            cursor.execute("""
                UPDATE auth_user SET role = %s, phone_number = %s, address = %s WHERE id = %s
            """, [user.role, phone, address, user.id])

            return JsonResponse({
                'message': 'User updated successfully.',
                'redirect_url': reverse('list_users')  # 👈 Redirect after edit
            })
        else:
            user = User.objects.create_user(
                username=email, email=email, password=phone,
                first_name=fname, last_name=lname
            )

            # Update extra fields
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE auth_user SET role = %s, phone_number = %s, address = %s WHERE id = %s
            """, [role, phone, address, user.id])

            msg = 'User created successfully.'
            subject = "Your Owner Account Has Been Created"
            message = f"""
            Hello {user.first_name},

            An account has been created for you as an Owner on the Women Safety Platform.

            Username: {user.email}
            Temporary Password: {phone}

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
                [user.email],
                fail_silently=False,
            )

            html = render_to_string("users/manage_user_form_inner.html", {
                'target_user': None,
                'button_text': 'Add'
            }, request=request)

            return JsonResponse({
                'message': msg,
                'html': html
            })

    # GET request: render full page
    button_text = "Update" if is_edit else "Add"
    return render(request, "users/manage_user.html", {
        'target_user': user,
        'button_text': button_text
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
            # Create user
            user = User.objects.create_user(
                username=owner.email,
                email=owner.email,
                password='1234',
                first_name=owner.first_name,
                last_name=owner.last_name,
            )
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE auth_user SET role = %s, phone_number = %s, address = %s WHERE id = %s
            """, ["owner", owner.phone, owner.address, user.id])

            # mail sending code

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
            # Delete from OwnerRequests
            owner.delete()

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
    users = User.objects.raw("SELECT * FROM auth_user WHERE role IN ('admin', 'owner') and is_active=1 ORDER BY date_joined DESC")
    return render(request, 'users/list_user.html', {'users': users})