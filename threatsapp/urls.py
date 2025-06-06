from django.urls import path
from . import views
urlpatterns = [
    path("manage/", views.manageThreats, name='manage_threats'),
    # path("view/threats",views.viewThreats,name="view_threats")
]
