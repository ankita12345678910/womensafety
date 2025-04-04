from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def manageUser(request):
    return HttpResponse("manage user")


def homePage(request):
    return render(request, 'home/index.html')


def requestOwner(request):
    return render(request, 'users/owner_request.html')
