from django.urls import path
from . import views
urlpatterns = [
    path("manage/user/<id>", views.manageUser,name='manage_user'),
    path("owner/request", views.requestOwner,name='owner_request'),
    path("", views.homePage, name='home')
]
