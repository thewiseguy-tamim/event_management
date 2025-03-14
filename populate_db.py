import os
import django

# Set up Django environment BEFORE importing models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "event_management.settings")
django.setup()

# Now import Django models
from django.contrib.auth.models import User
from eventapp.models import Event, Category, RSVP

# Example Data Population
def populate():
    # Create categories
    tech_category, _ = Category.objects.get_or_create(name="Technology", description="Tech events and meetups")
    music_category, _ = Category.objects.get_or_create(name="Music", description="Concerts and music festivals")

    # Create an organizer user
    organizer, _ = User.objects.get_or_create(username="admin", defaults={"email": "admin@example.com"})

    # Create events
    event1, _ = Event.objects.get_or_create(
        name="Tech Conference 2025",
        description="A conference about the latest in tech.",
        date="2025-05-15",
        time="10:00:00",
        location="Tech Hub, City Center",
        category=tech_category,
        organizer=organizer
    )

    event2, _ = Event.objects.get_or_create(
        name="Rock Fest",
        description="A festival featuring top rock bands.",
        date="2025-06-10",
        time="18:00:00",
        location="Music Arena",
        category=music_category,
        organizer=organizer
    )

    print("Database populated successfully!")

if __name__ == "__main__":
    populate()
