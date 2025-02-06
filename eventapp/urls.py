from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  
    path("create_entry/", views.create_entry, name="create_entry"),
    path('dashboard/', views.dashboard, name='dashboard'),
    
]

