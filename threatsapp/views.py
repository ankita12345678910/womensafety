from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def manageThreats(request):
    return HttpResponse("manage threats")