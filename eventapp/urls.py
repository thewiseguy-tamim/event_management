from django.urls import path
from .views import DashboardView, EventCreateView, HomeView, EventActionView, RSVPEventView, ParticipantDashboardView
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('create/', EventCreateView.as_view(), name='create_event'),
    path('', HomeView.as_view(), name='home'),
    path('event/<int:event_id>/action/', EventActionView.as_view(), name='event_action'),
    path('event/<int:event_id>/rsvp/', RSVPEventView.as_view(), name='rsvp_event'),
    path('my-events/', ParticipantDashboardView.as_view(), name='participant_dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


