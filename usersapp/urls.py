from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path("manage/user/<id>", views.manageUser,name='manage_user'),
    path("owner/request", views.requestOwner,name='owner_request'),
    path("", views.homePage, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.adminDashboard, name='dashboard'),
    path('list/request/owner', views.listOwnerRequest, name='list_request'),
    path('ajax/fetch/owner/data/<id>', views.getOwnerDetailsByAjax, name='ajax_fetch_owner_data'),
    path('ajax/update/owner/status/<int:id>/<str:status>/', views.updateOwnerStatus, name='ajax_update_owner_status'),
    path('list/users', views.listUsers, name='list_users'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
]
