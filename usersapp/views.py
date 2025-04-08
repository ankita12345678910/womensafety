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

# Create your views here.


@login_required
def adminDashboard(request):
    return render(request, 'users/admin_dashboard.html')


def manageUser(request, id=None):
    is_edit = id and int(id) != -1
    user = None
    if is_edit:
        title = "Edit user"
        user = User.objects.raw("select * from auth_user where id=%s", [id])[0]
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
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
            if password:
                user.set_password(password)
            user.save()
            msg = 'User updated successfully.'
        else:
            user = User.objects.create_user(
                username=email, email=email, password=password,
                first_name=fname, last_name=lname
            )
            msg = 'User created successfully.'

        # Update extra fields
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE auth_user SET role = %s, phone_number = %s, address = %s WHERE id = %s
        """, [role, phone, address, user.id])

        messages.success(request, msg)

    button_text = "Update" if is_edit else "Add"
    return render(request, "users/manage_user.html", {
        'user': user,
        'button_text': button_text
    })


def homePage(request):
    return render(request, 'home/index.html')


def requestOwner(request):
    if request.method == "POST":
        email_id = request.POST.get('email')
        exist_user = OwnerRequests.objects.filter(email=email_id)
        if exist_user is None:
            exist_user = User.objects.get(username=email_id)
            if exist_user is None:

                fname = request.POST.get('first_name')
                lname = request.POST.get('last_name')
                phone = request.POST.get('phone')
                business = request.POST.get('business_details')
                address = request.POST.get('address')
                invoice_file = request.FILES.get('invoice')
                invoice_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
                custom_filename = str(int(uuid.uuid4().hex[:5], 16) % 100000).zfill(
                    5)+"-"+invoice_file.name
                file_path = os.path.join(invoice_dir, custom_filename)
                fs = FileSystemStorage(location=invoice_dir)
                filename = fs.save(custom_filename, invoice_file)
                file_url = fs.url(filename)
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
            else:
                messages.error(
                    request, 'This email is already used,try with another email!')
        else:
            messages.error(
                request, 'This email is already used,try with another email!')

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
