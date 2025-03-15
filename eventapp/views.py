from django.shortcuts import render, redirect
from .models import Event, Category
from .forms import EventCreationForm, RSVPForm
from django.utils import timezone
from django.db.models import Count, Sum
from django.contrib import messages
from datetime import datetime
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import Event, Category, RSVP
from .forms import EventCreationForm, RSVPForm

@login_required(login_url='/user/sign-in/')
def dashboard(request):

    events = Event.objects.prefetch_related("participants")
    participants = User.objects.all()
    categories = Category.objects.all()


    print("Events:", events)
    print("Participants:", participants)
    print("Categories:", categories)

   
    today = timezone.now().date()

    
    filter_type = request.GET.get('filter', 'all')  

    if filter_type == 'upcoming':
        events = events.filter(date__gte=today)
    elif filter_type == 'past':
        events = events.filter(date__lt=today)
    
   
    total_participants = events.annotate(num_participants=Count('participants')).aggregate(total=Sum('num_participants'))['total'] or 0

    
    total_events = events.count()
    upcoming_events = events.filter(date__gte=today).count()
    past_events = events.filter(date__lt=today).count()
    today_events = events.filter(date=today)
    
    context = {
        'total_participants': total_participants,
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'today_events': today_events,
        'events': events,
        'participants': participants,
        'categories': categories,
        'filter': filter_type,
        'nums': range(3)
    }

    return render(request, 'dashboard.html', context)

def organizer_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (
            request.user.groups.filter(name='Admin').exists() or 
            request.user.groups.filter(name='Organizer').exists()
        ):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Access denied. Organizer privileges required.")
            return redirect('home')
    return _wrapped_view

@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventCreationForm(request.POST, request.FILES)  
        if form.is_valid():
            event = form.save(commit=False) 
            event.organizer = request.user  
            event.save()  
            return redirect('home')  
    else:
        form = EventCreationForm()

    return render(request, 'create_event.html', {'form': form})



def home(request):
    
    events = Event.objects.all()
    

    return render(request, 'home.html', {'events': events})

@login_required
def event_action(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    print(request.user.groups.all()) 
    print(f"Logged-in user: {request.user}")  
    print(f"Event organizer: {event.organizer}")  
    print(request.POST)  

    if request.method == "POST":
        if "edit" in request.POST:
  
            event.name = request.POST.get("name", event.name)
            event.date = request.POST.get("date", event.date)
            event.location = request.POST.get("location", event.location)
            event.save()
            messages.success(request, "Event updated successfully!")
            return redirect("dashboard")

        elif "join" in request.POST and request.user not in event.participants.all():

            event.participants.add(request.user)


            subject = "You have joined an event!"
            message = f"Hello {request.user.username},\n\nYou have successfully joined the event: {event.name}.\n\nDate: {event.date}\nLocation: {event.location}\n\nThank you!"
            recipient_email = request.user.email
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email], fail_silently=False)

            messages.success(request, "You joined the event! A confirmation email has been sent.")
            return redirect("dashboard")

        elif "delete" in request.POST:
 
            event.delete()
            messages.success(request, "Event deleted successfully!")
            return redirect("dashboard")

  
    return redirect("dashboard")

@login_required
def rsvp_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    

    existing_rsvp = RSVP.objects.filter(user=request.user, event=event).first()
    
    if request.method == 'POST':
        form = RSVPForm(request.POST, instance=existing_rsvp)
        if form.is_valid():
            rsvp = form.save(commit=False)
            
            if not existing_rsvp:
                rsvp.user = request.user
                rsvp.event = event
            
            rsvp.save()
            
            # Add user to participants if they responded 'Yes'
            if rsvp.response:
                event.participants.add(request.user)
            else:
                # Remove from participants if they responded 'No'
                event.participants.remove(request.user)
            
            # Send confirmation email
            subject = f"RSVP Confirmation for {event.name}"
            message = f"Hello {request.user.username},\n\n"
            message += f"Your RSVP for {event.name} has been received.\n\n"
            message += f"Your response: {'Attending' if rsvp.response else 'Not Attending'}\n"
            message += f"Event details:\n"
            message += f"Date: {event.date}\n"
            message += f"Time: {event.time or 'Not specified'}\n"
            message += f"Location: {event.location}\n\n"
            message += "Thank you!"
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False
            )
            
            messages.success(request, "Your RSVP has been recorded. A confirmation email has been sent.")
            return redirect('dashboard')
    else:
        form = RSVPForm(instance=existing_rsvp)
    
    return render(request, 'rsvp_event.html', {
        'form': form,
        'event': event,
        'existing_rsvp': existing_rsvp
    })


@login_required
def participant_dashboard(request):

    rsvp_events = RSVP.objects.filter(user=request.user, response=True).select_related('event')
    

    participating_events = request.user.events_participating.all()
    

    all_events = set()
    for rsvp in rsvp_events:
        all_events.add(rsvp.event)
    
    for event in participating_events:
        all_events.add(event)
    
    return render(request, 'participant_dashboard.html', {
        'events': all_events
    })