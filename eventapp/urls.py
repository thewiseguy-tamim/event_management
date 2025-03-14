from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),  
    path('create_event/', views.create_event, name='create_event'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('event/<int:event_id>/action/', views.event_action, name='event_action'),  
    path('event/<int:event_id>/rsvp/', views.rsvp_event, name='rsvp_event'),
    path('my-events/', views.participant_dashboard, name='participant_dashboard'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


