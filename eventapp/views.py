from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, ListView, View, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Sum
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Event, Category, RSVP
from .forms import EventCreationForm, RSVPForm
from django.contrib.auth.models import User

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    login_url = '/user/sign-in/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events = Event.objects.prefetch_related("participants")
        participants = User.objects.all()
        categories = Category.objects.all()
        today = timezone.now().date()
        filter_type = self.request.GET.get('filter', 'all')

        if filter_type == 'upcoming':
            events = events.filter(date__gte=today)
        elif filter_type == 'past':
            events = events.filter(date__lt=today)

        total_participants = events.annotate(
            num_participants=Count('participants')
        ).aggregate(total=Sum('num_participants'))['total'] or 0

        context.update({
            'total_participants': total_participants,
            'total_events': events.count(),
            'upcoming_events': events.filter(date__gte=today).count(),
            'past_events': events.filter(date__lt=today).count(),
            'today_events': events.filter(date=today),
            'events': events,
            'participants': participants,
            'categories': categories,
            'filter': filter_type,
            'nums': range(3)
        })
        return context

class OrganizerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.groups.filter(name='Admin').exists() or 
                request.user.groups.filter(name='Organizer').exists()):
            messages.error(request, "Access denied. Organizer privileges required.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventCreationForm
    template_name = 'create_event.html'
    login_url = '/user/sign-in/'

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('home')

class HomeView(ListView):
    model = Event
    template_name = 'home.html'
    context_object_name = 'events'

class EventActionView(LoginRequiredMixin, View):
    login_url = '/user/sign-in/'

    def post(self, request, *args, **kwargs):
        event = get_object_or_404(Event, id=kwargs['event_id'])

        if 'edit' in request.POST or 'delete' in request.POST:
            if not (request.user == event.organizer or request.user.groups.filter(name='Admin').exists()):
                messages.error(request, "Access denied. Organizer privileges required.")
                return redirect('dashboard')

            if 'edit' in request.POST:
                event.name = request.POST.get('name', event.name)
                event.date = request.POST.get('date', event.date)
                event.location = request.POST.get('location', event.location)
                event.save()
                messages.success(request, "Event updated successfully!")
            elif 'delete' in request.POST:
                event.delete()
                messages.success(request, "Event deleted successfully!")

        elif 'join' in request.POST:
            if request.user not in event.participants.all():
                event.participants.add(request.user)
                send_mail(
                    "You have joined an event!",
                    f"Hello {request.user.username},\n\nYou joined {event.name}.",
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=False
                )
                messages.success(request, "You joined the event! Confirmation email sent.")
            else:
                messages.warning(request, "You're already a participant.")

        return redirect('dashboard')

class RSVPEventView(LoginRequiredMixin, FormView):
    form_class = RSVPForm
    template_name = 'rsvp_event.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.event = get_object_or_404(Event, id=self.kwargs['event_id'])
        self.existing_rsvp = RSVP.objects.filter(
            user=self.request.user, 
            event=self.event
        ).first()
        kwargs['instance'] = self.existing_rsvp
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        context['existing_rsvp'] = self.existing_rsvp
        return context

    def form_valid(self, form):
        rsvp = form.save(commit=False)
        if not self.existing_rsvp:
            rsvp.user = self.request.user
            rsvp.event = self.event
        rsvp.save()

        if rsvp.response:
            self.event.participants.add(self.request.user)
        else:
            self.event.participants.remove(self.request.user)

        send_mail(
            f"RSVP Confirmation for {self.event.name}",
            f"Hello {self.request.user.username},\n\nRSVP: {'Attending' if rsvp.response else 'Not Attending'}",
            settings.DEFAULT_FROM_EMAIL,
            [self.request.user.email],
            fail_silently=False
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard')

class ParticipantDashboardView(LoginRequiredMixin, ListView):
    template_name = 'participant_dashboard.html'
    context_object_name = 'events'

    def get_queryset(self):
        rsvp_events = Event.objects.filter(
            rsvp__user=self.request.user, 
            rsvp__response=True
        )
        participating_events = self.request.user.events_participating.all()
        return rsvp_events.union(participating_events)