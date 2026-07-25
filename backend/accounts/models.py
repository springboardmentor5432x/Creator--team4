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
    
    # YouTube fields
    youtube_channel_id = models.CharField(max_length=255, blank=True, null=True)
    youtube_channel_title = models.CharField(max_length=255, blank=True, null=True)
    
    # LinkedIn fields
    linkedin_profile_id = models.CharField(max_length=255, blank=True, null=True)
    linkedin_profile_title = models.CharField(max_length=255, blank=True, null=True)
    linkedin_profile_headline = models.CharField(max_length=500, blank=True, null=True)
    linkedin_profile_picture = models.CharField(max_length=1000, blank=True, null=True)
    linkedin_profile_banner = models.CharField(max_length=1000, blank=True, null=True)
    linkedin_connections_count = models.IntegerField(default=0)
    linkedin_profile_views = models.IntegerField(default=0)
    linkedin_post_impressions = models.IntegerField(default=0)
    linkedin_search_appearances = models.IntegerField(default=0)

    # Instagram fields
    instagram_profile_id = models.CharField(max_length=255, blank=True, null=True)
    instagram_profile_title = models.CharField(max_length=255, blank=True, null=True)
    instagram_profile_picture = models.CharField(max_length=1000, blank=True, null=True)
    instagram_followers_count = models.IntegerField(default=0)
    instagram_engagement_rate = models.FloatField(default=0.0)
    instagram_posts_count = models.IntegerField(default=0)
    instagram_verified_meta = models.BooleanField(default=False)

    # Facebook fields
    facebook_page_id = models.CharField(max_length=255, blank=True, null=True)
    facebook_page_title = models.CharField(max_length=255, blank=True, null=True)
    facebook_page_picture = models.CharField(max_length=1000, blank=True, null=True)
    facebook_followers_count = models.IntegerField(default=0)
    facebook_reach_count = models.IntegerField(default=0)
    facebook_engagement_rate = models.FloatField(default=0.0)
    facebook_verified_meta = models.BooleanField(default=False)

    # Twitter / X fields
    twitter_profile_id = models.CharField(max_length=255, blank=True, null=True)
    twitter_username = models.CharField(max_length=255, blank=True, null=True)
    twitter_display_name = models.CharField(max_length=255, blank=True, null=True)
    twitter_profile_picture = models.CharField(max_length=1000, blank=True, null=True)
    twitter_followers_count = models.IntegerField(default=0)
    twitter_following_count = models.IntegerField(default=0)
    twitter_tweets_count = models.IntegerField(default=0)
    twitter_engagement_rate = models.FloatField(default=0.0)
    twitter_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class GrowthReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=255)
    platforms = models.CharField(max_length=255)  # e.g., "youtube,linkedin,instagram,facebook"
    report_type = models.CharField(max_length=50, default='Growth & Trend')
    created_at = models.DateTimeField(auto_now_add=True)
    data_json = models.TextField()  # Snapshotted metrics JSON

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class WorkflowPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workflows')
    title = models.CharField(max_length=255)
    caption = models.TextField(blank=True, null=True)
    media_url = models.CharField(max_length=1000, blank=True, null=True)
    selected_platforms = models.CharField(max_length=255)  # e.g., "youtube,linkedin,instagram,facebook"
    scheduled_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=50, default='Draft')  # Draft, Scheduled, Published, Failed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.status}"

class SponsorshipDeal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deals')
    brand = models.CharField(max_length=255)
    title = models.CharField(max_length=500)
    source = models.CharField(max_length=100, default='Sponsorships')
    platform = models.CharField(max_length=100)
    payout = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=50, default='In Negotiation')
    due_date = models.DateField(blank=True, null=True)
    deliverables = models.TextField(blank=True, null=True)
    invoice_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} - {self.title}"

class AudienceInsightProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audience_profiles')
    platform = models.CharField(max_length=50) # 'youtube', 'instagram', 'facebook', 'linkedin', 'twitter'
    age_demographics_json = models.TextField(blank=True, null=True)
    gender_split_json = models.TextField(blank=True, null=True)
    top_regions_json = models.TextField(blank=True, null=True)
    device_analytics_json = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.platform} Audience - {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        role = 'Administrator' if instance.is_superuser else 'Creator'
        UserProfile.objects.get_or_create(user=instance, defaults={'role': role})

