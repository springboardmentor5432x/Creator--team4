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
    linkedin_connect_view, linkedin_disconnect_view,
    instagram_connect_view, instagram_disconnect_view, instagram_analytics_view,
    facebook_connect_view, facebook_disconnect_view, facebook_analytics_view,
    twitter_connect_view, twitter_disconnect_view, twitter_analytics_view,
    list_reports_view, generate_report_view, delete_report_view,
    list_workflows_view, create_workflow_view, edit_workflow_view, publish_workflow_view, delete_workflow_view,
    list_deals_view,
    create_deal_view,
    delete_deal_view,
    get_audience_insights_view,
    me_view
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
    
    # YouTube
    path('api/users/connect-youtube/', connect_youtube_view, name='api_connect_youtube'),
    path('api/users/disconnect-youtube/', disconnect_youtube_view, name='api_disconnect_youtube'),
    path('api/youtube/channel/', youtube_channel_analytics, name='api_youtube_channel'),
    
    # LinkedIn
    path('api/users/connect-linkedin/', linkedin_connect_view, name='api_connect_linkedin'),
    path('api/users/disconnect-linkedin/', linkedin_disconnect_view, name='api_disconnect_linkedin'),
    
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
    
    path('api/config/', get_config, name='api_config'),
    path('api/health', health_check, name='api_health'),
    path('api/me/', me_view, name='api_me'),
    
    # Serve React SPA Frontend (raw file, not Django template)
    path('', serve_frontend, name='frontend'),
]

