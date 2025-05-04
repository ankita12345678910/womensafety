from django.urls import path
from . import views

urlpatterns = [
   path('cameras/manage/<id>/', views.manageCamera, name='manage_camera'),
]
