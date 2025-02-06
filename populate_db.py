import os
import django
from faker import Faker
import random
from eventapp.models import Event, Participant, Category

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

def populate_db():
    fake = Faker()

    # Create Categories
    categories = [Category.objects.create(
        name=fake.word().capitalize(),
        description=fake.sentence()
    ) for _ in range(10)]
    print(f"Created {len(categories)} categories.")

    # Create Events
    events = [Event.objects.create(
        name=fake.sentence(nb_words=4),
        description=fake.paragraph(),
        date=fake.date_this_year(),
        time=fake.time(),
        location=fake.city(),
        category=random.choice(categories)
    ) for _ in range(20)]
    print(f"Created {len(events)} events.")

    # Create Participants
    participants = []
    for _ in range(10000):
        participant = Participant.objects.create(
            name=fake.name(),
            email=fake.unique.email()
        )
        event = random.choice(events)
        participant.events.add(event)
        participants.append(participant)
    print(f"Created {len(participants)} participants.")

    print("Database populated successfully!")

if __name__ == "__main__":
    populate_db()
