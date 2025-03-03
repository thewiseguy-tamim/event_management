from django.urls import path
from . import views

urlpatterns = [
    path('sign-up/', views.sign_up, name='sign-up'),
    path('sign-in/', views.sign_in, name='login'),
    path('sign-out/', views.sign_out, name='logout'),
    path('base/', views.base_view, name='base'),
    path('admin_dash/', views.admin_dashboard, name='admin-dashboard'),
    path("create_group/", views.create_group, name="create_group"),
    path('assing-role/<int:user_id>/', views.assing_role, name='assing-role'),
    path('group_list/', views.group_list, name='group_list'),
    path('activate/<int:uid>/<str:token>/', views.activate, name='activate')
]