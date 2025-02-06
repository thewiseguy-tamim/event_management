from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Participant(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    events = models.ManyToManyField(Event, related_name='participants')

    def __str__(self):
        return self.name

