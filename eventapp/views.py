from django.shortcuts import render, redirect
from .models import Event, Participant, Category
from .forms import EventForm, ParticipantForm, CategoryForm
from django.utils import timezone
from django.db.models import Count, Sum
from django.contrib import messages

def dashboard(request):

    events = Event.objects.prefetch_related("participants")
    participants = Participant.objects.all()
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
    }

    return render(request, 'dashboard.html', context)

def home(request):
    return render(request, 'home.html')

def create_entry(request):
    if request.method == 'POST':
        entry_type = request.POST.get('entry_type')

        if entry_type == "event":
            form = EventForm(request.POST)
        elif entry_type == "participant":
            form = ParticipantForm(request.POST)
        elif entry_type == "category":
            form = CategoryForm(request.POST)
        else:
            messages.error(request, "Invalid form selection")
            return redirect('create_entry')

        if form.is_valid():
            form.save()
            messages.success(request, "Entry added successfully!")
            return redirect('create_entry')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EventForm()  

    return render(request, 'forum.html', {
        'event_form': EventForm(),
        'participant_form': ParticipantForm(),
        'category_form': CategoryForm(),
    })
