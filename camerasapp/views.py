from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def manageCameras(request):
    return HttpResponse("manage cameras")
