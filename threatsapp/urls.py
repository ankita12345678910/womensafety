from django.urls import path
from . import views
urlpatterns = [
    path("manage/",views.manageThreats)
]