from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('Creator', 'Creator'),
        ('Agency', 'Agency'),
        ('Marketing Team', 'Marketing Team'),
        ('Administrator', 'Administrator'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Creator')
    youtube_channel_id = models.CharField(max_length=255, blank=True, null=True)
    youtube_channel_title = models.CharField(max_length=255, blank=True, null=True)
    linkedin_profile_id = models.CharField(max_length=255, blank=True, null=True)
    linkedin_profile_title = models.CharField(max_length=255, blank=True, null=True)
    linkedin_profile_picture = models.CharField(max_length=1000, blank=True, null=True)
    linkedin_profile_banner = models.CharField(max_length=1000, blank=True, null=True)
    linkedin_connections_count = models.IntegerField(default=0)
    linkedin_profile_views = models.IntegerField(default=0)
    linkedin_post_impressions = models.IntegerField(default=0)
    linkedin_search_appearances = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        role = 'Administrator' if instance.is_superuser else 'Creator'
        UserProfile.objects.get_or_create(user=instance, defaults={'role': role})

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    role = 'Administrator' if instance.is_superuser else 'Creator'
    UserProfile.objects.get_or_create(user=instance, defaults={'role': role})
    instance.profile.save()
