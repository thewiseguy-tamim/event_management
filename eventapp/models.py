from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name='events_participating', blank=True)
    image = models.ImageField(
        upload_to='event_images/',
        default='event_images/default_event.png'  
    )

    def __str__(self):
        return self.name

class RSVP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    response = models.BooleanField(default=False)  

    def __str__(self):
        return f"{self.user.username} RSVP for {self.event.name}"