from django.shortcuts import render, redirect
from .models import Event, Category
from .forms import EventCreationForm, RSVPForm
from django.utils import timezone
from django.db.models import Count, Sum
from django.contrib import messages
from datetime import datetime
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event
from django.core.mail import send_mail
from django.conf import settings


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

def rsvp_event(request):
    if request.method == 'POST':
        form = RSVPForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  
    else:
        form = RSVPForm()

    return render(request, 'rsvp_event.html', {'form': form})

def home(request):
    
    events = Event.objects.all()
    

    return render(request, 'home.html', {'events': events})

@login_required
def event_action(request, event_id):
    event = get_object_or_404(Event, id=event_id)


    if request.method == "POST" and "edit" in request.POST and request.user == event.organizer:
        event.name = request.POST.get("name", event.name)
        event.date = request.POST.get("date", event.date)
        event.location = request.POST.get("location", event.location)
        event.save()
        messages.success(request, "Event updated successfully!")
        return redirect("dashboard")

    elif request.method == "POST" and "join" in request.POST and request.user not in event.participants.all():
        event.participants.add(request.user)

        subject = "You have joined an event!"
        message = f"Hello {request.user.username},\n\nYou have successfully joined the event: {event.name}.\n\nDate: {event.date}\nLocation: {event.location}\n\nThank you!"
        recipient_email = request.user.email  
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email], fail_silently=False)

        messages.success(request, "You joined the event! A confirmation email has been sent.")
        return redirect("dashboard")


    elif request.method == "POST" and "delete" in request.POST and request.user == event.organizer:
        event.delete()
        messages.success(request, "Event deleted successfully!")
        return redirect("dashboard")

    return redirect("dashboard")