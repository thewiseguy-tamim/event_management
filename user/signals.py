from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import Group, User
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

@receiver(post_save, sender=User)
def assign_role(sender, instance, created, **kwargs):
    if created:
        user_group, created = Group.objects.get_or_create(name='User')
        instance.groups.add(user_group)
        instance.save()

