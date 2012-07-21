from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Profile(models.Model):
    user = models.OneToOneField(User)

    # Fields used for user activation after signup
    activation_key = models.CharField(max_length=40, blank=True)
    key_expires = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return '%s %s (%s)' % (self.user.first_name, self.user.last_name, self.user.username)


def create_user_profile(sender, instance, created, **kwargs):
    # Create user profile for user after creation
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
