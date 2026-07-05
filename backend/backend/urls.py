"""
URL configuration for backend project.
"""
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from pathlib import Path
from accounts.views import register_view, login_view, google_login_view, list_users_view, update_user_role_view, health_check

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
    path('api/health', health_check, name='api_health'),
    
    # Serve React SPA Frontend (raw file, not Django template)
    path('', serve_frontend, name='frontend'),
]

