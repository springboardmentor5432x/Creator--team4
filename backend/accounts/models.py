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

class AgencyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agency_profile')
    agency_name = models.CharField(max_length=255, default='Apex Creator Management')
    logo_url = models.CharField(max_length=1000, blank=True, null=True)
    commission_rate = models.FloatField(default=15.0)  # Default 15% agency cut
    contact_email = models.CharField(max_length=255, blank=True, null=True)
    currency = models.CharField(max_length=10, default='₹')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.agency_name} ({self.user.username})"

class AgencyCreatorRelation(models.Model):
    agency = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_creators')
    creator_name = models.CharField(max_length=255)
    handle = models.CharField(max_length=255)
    category = models.CharField(max_length=100, default='Tech & Gaming')
    primary_platform = models.CharField(max_length=100, default='YouTube')
    followers_count = models.IntegerField(default=500000)
    engagement_rate = models.FloatField(default=4.5)
    monthly_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=150000.00)
    commission_split = models.FloatField(default=15.0) # Agency cut %
    assigned_manager = models.CharField(max_length=255, default='Priya Sharma')
    sponsorship_rate = models.DecimalField(max_digits=12, decimal_places=2, default=150000.00)
    status = models.CharField(max_length=50, default='Active') # Active, Pending, Archived
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.creator_name} (@{self.handle}) - {self.agency.username}"

class AgencyCampaign(models.Model):
    agency = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agency_campaigns')
    campaign_name = models.CharField(max_length=255)
    brand_name = models.CharField(max_length=255)
    total_budget = models.DecimalField(max_digits=12, decimal_places=2, default=500000.00)
    target_reach = models.IntegerField(default=1000000)
    achieved_reach = models.IntegerField(default=850000)
    status = models.CharField(max_length=50, default='Active') # Active, Draft, Completed
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.campaign_name} ({self.brand_name})"

class AgencyCampaignCreator(models.Model):
    campaign = models.ForeignKey(AgencyCampaign, on_delete=models.CASCADE, related_name='participating_creators')
    creator_relation = models.ForeignKey(AgencyCreatorRelation, on_delete=models.CASCADE, related_name='campaign_assignments')
    deliverable = models.CharField(max_length=255, default='1 Dedicated YouTube Video + 2 IG Reels')
    payout = models.DecimalField(max_digits=12, decimal_places=2, default=75000.00)
    deliverable_status = models.CharField(max_length=50, default='In Progress') # Pending, In Progress, Approved, Published

    def __str__(self):
        return f"{self.creator_relation.creator_name} in {self.campaign.campaign_name}"

class SocialPlatformAccount(models.Model):
    PLATFORM_CHOICES = [
        ('youtube', 'YouTube'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'X (Twitter)'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_accounts')
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    platform_user_id = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    avatar_url = models.CharField(max_length=1000, blank=True, null=True)
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)
    is_connected = models.BooleanField(default=True)
    connected_at = models.DateTimeField(auto_now_add=True)
    last_synced_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'platform')

    def __str__(self):
        return f"{self.user.username} - {self.platform} (@{self.username or self.platform_user_id})"

class PlatformAnalyticsSnapshot(models.Model):
    account = models.ForeignKey(SocialPlatformAccount, on_delete=models.CASCADE, related_name='snapshots')
    followers_subscribers = models.IntegerField(default=0)
    total_views = models.BigIntegerField(default=0)
    reach = models.BigIntegerField(default=0)
    impressions = models.BigIntegerField(default=0)
    engagement_rate = models.FloatField(default=0.0)
    posts_count = models.IntegerField(default=0)
    raw_response = models.TextField(blank=True, null=True)  # JSON dump
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.account.platform} Snapshot - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class ContentItemAnalytics(models.Model):
    CONTENT_TYPES = [
        ('video', 'Video'),
        ('reel', 'Reel'),
        ('post', 'Post'),
        ('tweet', 'Tweet'),
    ]
    account = models.ForeignKey(SocialPlatformAccount, on_delete=models.CASCADE, related_name='content_items')
    platform = models.CharField(max_length=50)
    content_id = models.CharField(max_length=255)
    title = models.CharField(max_length=500)
    content_type = models.CharField(max_length=50, choices=CONTENT_TYPES, default='post')
    thumbnail_url = models.CharField(max_length=1000, blank=True, null=True)
    content_url = models.CharField(max_length=1000, blank=True, null=True)
    views = models.BigIntegerField(default=0)
    likes = models.BigIntegerField(default=0)
    comments = models.BigIntegerField(default=0)
    shares = models.BigIntegerField(default=0)
    watch_time_minutes = models.FloatField(default=0.0)
    reach = models.BigIntegerField(default=0)
    impressions = models.BigIntegerField(default=0)
    engagement_rate = models.FloatField(default=0.0)
    published_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('account', 'content_id')

    def __str__(self):
        return f"[{self.platform}] {self.title} ({self.views} views)"

class SyncHistoryLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sync_logs')
    platform = models.CharField(max_length=50, default='all')  # 'all', 'youtube', 'instagram', etc.
    sync_type = models.CharField(max_length=50, default='manual')  # 'manual' or 'scheduled'
    status = models.CharField(max_length=50, default='Success')  # 'Success', 'Failed', 'In Progress'
    items_synced = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.platform} ({self.status}) @ {self.started_at}"

class AutoSyncConfig(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sync_config')
    interval_minutes = models.IntegerField(default=360)  # Default 6 hours (360 mins)
    auto_sync_enabled = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(blank=True, null=True)
    next_run_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Sync Settings ({self.interval_minutes}m, Active={self.auto_sync_enabled})"

class SystemNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    category = models.CharField(max_length=50, default='performance')  # 'performance', 'engagement', 'revenue', 'weekly_summary'
    severity = models.CharField(max_length=50, default='info')  # 'info', 'success', 'warning', 'critical'
    is_read = models.BooleanField(default=False)
    action_link = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.category.upper()}] {self.title} - {self.user.username}"

class ScheduledReportSchedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_schedules')
    title = models.CharField(max_length=255, default='Weekly Analytics Summary')
    frequency = models.CharField(max_length=50, default='weekly')  # 'daily', 'weekly', 'monthly'
    export_format = models.CharField(max_length=50, default='PDF')  # 'PDF', 'CSV', 'JSON'
    email_recipients = models.TextField(blank=True, null=True)  # Comma separated email addresses
    is_active = models.BooleanField(default=True)
    last_generated_at = models.DateTimeField(blank=True, null=True)
    next_run_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.frequency}, {self.export_format}) - {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        role = 'Administrator' if instance.is_superuser else 'Creator'
        UserProfile.objects.get_or_create(user=instance, defaults={'role': role})
        AutoSyncConfig.objects.get_or_create(user=instance)




