from django.urls import path
from . import views
from .views import RoleBasedLoginView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("manage/user/<id>", views.manageUser,name='manage_user'),
    path("owner/request", views.requestOwner,name='owner_request'),
    path("", views.homePage, name='home'),
    path('login/', RoleBasedLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('admin/dashboard/', views.adminDashboard, name='admin_dashboard'),
    path('owner/dashboard/', views.ownerDashboard, name='owner_dashboard'),
    path('viewer/dashboard/', views.viewerDashboard, name='viewer_dashboard'),
    path('list/request/owner', views.listOwnerRequest, name='list_request'),
    path('ajax/fetch/owner/data/<id>', views.getOwnerDetailsByAjax, name='ajax_fetch_owner_data'),
    path('ajax/update/owner/status/<int:id>/<str:status>/', views.updateOwnerStatus, name='ajax_update_owner_status'),
    path('list/users', views.listUsers, name='list_users'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
