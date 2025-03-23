from django.urls import path
from . import views
from .views import CustomPasswordResetView, CustomPasswordResetDoneView,CustomPasswordResetConfirmView,CustomPasswordResetCompleteView

urlpatterns = [
    path('sign-up/', views.sign_up, name='sign-up'),
    path('sign-in/', views.sign_in, name='login'),
    path('sign-out/', views.sign_out, name='logout'),
    path('base/', views.base_view, name='base'),
    path('admin_dash/', views.admin_dashboard, name='admin-dashboard'),
    path("create_group/", views.create_group, name="create_group"),
    path('assing-role/<int:user_id>/', views.assing_role, name='assing-role'),
    path('group_list/', views.group_list, name='group_list'),
    path('activate/<int:uid>/<str:token>/', views.activate, name='activate'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-password-confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm' ),
    path('password-reset/complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]


