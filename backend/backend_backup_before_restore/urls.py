"""
URL configuration for backend project.
"""
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from pathlib import Path
from accounts.views import (
    register_view, login_view, google_login_view, list_users_view, update_user_role_view, health_check,
    youtube_channel_analytics, connect_youtube_view, disconnect_youtube_view, get_config,
    linkedin_connect_view, linkedin_disconnect_view, linkedin_analytics_view,
    instagram_connect_view, instagram_disconnect_view, instagram_analytics_view,
    facebook_connect_view, facebook_disconnect_view, facebook_analytics_view,
    twitter_connect_view, twitter_disconnect_view, twitter_analytics_view,
    list_reports_view, generate_report_view, delete_report_view,
    list_workflows_view, create_workflow_view, edit_workflow_view, publish_workflow_view, delete_workflow_view,
    list_deals_view,
    create_deal_view,
    delete_deal_view,
    get_audience_insights_view,
    me_view,
    get_agency_overview_view,
    manage_agency_creators_view,
    compare_agency_creators_view,
    get_agency_revenue_view,
    manage_agency_campaigns_view,
    manage_agency_settings_view,
    get_oauth_url_view,
    oauth_callback_view,
    disconnect_social_account_view,
    get_multi_platform_analytics_view,
    get_platform_wise_analytics_view,
    get_content_analytics_view,
    get_content_detail_view,
    trigger_sync_all_view,
    get_sync_history_view,
    manage_sync_settings_view,
    list_notifications_view,
    mark_notification_read_view,
    trigger_alert_evaluation_view,
    get_weekly_analytics_report_view,
    list_scheduled_reports_view,
    create_scheduled_report_view,
    export_report_data_view,
)


def serve_frontend(request):
    """Serve the React SPA without Django template processing (avoids JSX conflict)."""
    index_path = Path(__file__).resolve().parent.parent / 'templates' / 'index.html'
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return HttpResponse(content, content_type='text/html')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/register/', register_view, name='api_register'),
    path('api/login/', login_view, name='api_login'),
    path('api/google-login/', google_login_view, name='api_google_login'),
    path('api/users/', list_users_view, name='api_list_users'),
    path('api/users/update-role/', update_user_role_view, name='api_update_user_role'),
    
    # OAuth Authentication & Linking
    path('api/auth/oauth-url/<str:platform>/', get_oauth_url_view, name='api_oauth_url'),
    path('api/auth/oauth-callback/<str:platform>/', oauth_callback_view, name='api_oauth_callback'),
    path('api/auth/disconnect/<str:platform>/', disconnect_social_account_view, name='api_disconnect_account'),

    # Multi-Platform & Platform-wise Analytics
    path('api/analytics/multi-platform/', get_multi_platform_analytics_view, name='api_multi_platform_analytics'),
    path('api/analytics/platform/<str:platform>/', get_platform_wise_analytics_view, name='api_platform_wise_analytics'),

    # Content Management Analytics
    path('api/analytics/content/', get_content_analytics_view, name='api_content_analytics'),
    path('api/analytics/content/<str:content_id>/', get_content_detail_view, name='api_content_detail'),

    # Scheduled Synchronization & Logs
    path('api/sync/all/', trigger_sync_all_view, name='api_sync_all'),
    path('api/sync/history/', get_sync_history_view, name='api_sync_history'),
    path('api/sync/settings/', manage_sync_settings_view, name='api_sync_settings'),

    # Notifications & Performance Alerts
    path('api/notifications/', list_notifications_view, name='api_notifications'),
    path('api/notifications/mark-read/', mark_notification_read_view, name='api_mark_notifications_read'),
    path('api/notifications/trigger-eval/', trigger_alert_evaluation_view, name='api_trigger_alert_evaluation'),

    # Weekly Analytics & Scheduled Reports
    path('api/reports/weekly/', get_weekly_analytics_report_view, name='api_weekly_report'),
    path('api/reports/scheduled/', list_scheduled_reports_view, name='api_scheduled_reports'),
    path('api/reports/scheduled/create/', create_scheduled_report_view, name='api_create_scheduled_report'),
    path('api/reports/export/', export_report_data_view, name='api_export_report_data'),


    # YouTube
    path('api/users/connect-youtube/', connect_youtube_view, name='api_connect_youtube'),
    path('api/users/disconnect-youtube/', disconnect_youtube_view, name='api_disconnect_youtube'),
    path('api/youtube/channel/', youtube_channel_analytics, name='api_youtube_channel'),
    
    # LinkedIn
    path('api/users/connect-linkedin/', linkedin_connect_view, name='api_connect_linkedin'),
    path('api/users/disconnect-linkedin/', linkedin_disconnect_view, name='api_disconnect_linkedin'),
    path('api/linkedin/analytics/', linkedin_analytics_view, name='api_linkedin_analytics'),

    # Instagram
    path('api/users/connect-instagram/', instagram_connect_view, name='api_connect_instagram'),
    path('api/users/disconnect-instagram/', instagram_disconnect_view, name='api_disconnect_instagram'),
    path('api/instagram/analytics/', instagram_analytics_view, name='api_instagram_analytics'),
    
    # Facebook
    path('api/users/connect-facebook/', facebook_connect_view, name='api_connect_facebook'),
    path('api/users/disconnect-facebook/', facebook_disconnect_view, name='api_disconnect_facebook'),
    path('api/facebook/analytics/', facebook_analytics_view, name='api_facebook_analytics'),

    # Twitter / X
    path('api/users/connect-twitter/', twitter_connect_view, name='api_connect_twitter'),
    path('api/users/disconnect-twitter/', twitter_disconnect_view, name='api_disconnect_twitter'),
    path('api/twitter/analytics/', twitter_analytics_view, name='api_twitter_analytics'),
    
    # Trend Reports
    path('api/reports/', list_reports_view, name='api_list_reports'),
    path('api/reports/generate/', generate_report_view, name='api_generate_report'),
    path('api/reports/delete/', delete_report_view, name='api_delete_report'),
    
    # Workflows
    path('api/workflows/', list_workflows_view, name='api_list_workflows'),
    path('api/workflows/create/', create_workflow_view, name='api_create_workflow'),
    path('api/workflows/edit/', edit_workflow_view, name='api_edit_workflow'),
    path('api/workflows/publish/', publish_workflow_view, name='api_publish_workflow'),
    path('api/workflows/delete/', delete_workflow_view, name='api_delete_workflow'),
    
    # Revenue Deals
    path('api/revenue/deals/', list_deals_view, name='api_list_deals'),
    path('api/revenue/deals/create/', create_deal_view, name='api_create_deal'),
    path('api/revenue/deals/delete/<str:deal_id>/', delete_deal_view, name='api_delete_deal'),
    
    # Audience Insights
    path('api/audience/insights/', get_audience_insights_view, name='api_audience_insights'),
    
    # Agency Dashboard
    path('api/agency/overview/', get_agency_overview_view, name='api_agency_overview'),
    path('api/agency/creators/', manage_agency_creators_view, name='api_agency_creators'),
    path('api/agency/compare/', compare_agency_creators_view, name='api_agency_compare'),
    path('api/agency/revenue/', get_agency_revenue_view, name='api_agency_revenue'),
    path('api/agency/campaigns/', manage_agency_campaigns_view, name='api_agency_campaigns'),
    path('api/agency/settings/', manage_agency_settings_view, name='api_agency_settings'),

    path('api/config/', get_config, name='api_config'),
    path('api/health', health_check, name='api_health'),
    path('api/me/', me_view, name='api_me'),
    
    # Serve React SPA Frontend (raw file, not Django template)
    path('', serve_frontend, name='frontend'),
]


