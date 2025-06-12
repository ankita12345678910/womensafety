from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("manage/", views.manageThreats, name='manage_threats'),
    # path("view/threats",views.viewThreats,name="view_threats")
    path('ajax/review/', views.ajax_review_threat, name='ajax_review_threat'),
    path('submit-review/', views.submit_review, name='submit_review'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
