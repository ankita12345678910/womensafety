from django.urls import path
from . import views

urlpatterns = [
   path('cameras/manage/<id>/', views.manageCamera, name='manage_camera'),
   path('list/', views.listCameras, name='list_cameras'),
   path('change-camera-status/<int:camera_id>/', views.change_camera_status, name='change_camera_status'),
]
