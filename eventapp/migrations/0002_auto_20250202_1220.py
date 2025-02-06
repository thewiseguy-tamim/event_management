from django.db import migrations
from datetime import date, timedelta

def create_sample_data(apps, schema_editor):
    Category = apps.get_model('eventapp', 'Category')
    Event = apps.get_model('eventapp', 'Event')
    Participant = apps.get_model('eventapp', 'Participant')

    # Create categories
    tech = Category.objects.create(name="Tech ", description="Technology events")
    music = Category.objects.create(name="Music ", description="Music events")

    # Create events
    future_event = Event.objects.create(
        name="Future Tech Summit",
        description="Explore future technologies",
        date=date.today() + timedelta(days=7),
        time="09:00:00",
        location="Convention Center",
        category=tech
    )
    # ... add other sample data

class Migration(migrations.Migration):
    dependencies = [
        ('eventapp', '0001_initial'),  # Replace with your initial migration
    ]
    operations = [
        migrations.RunPython(create_sample_data),
    ]