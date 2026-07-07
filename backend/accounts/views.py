import json
import os
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.utils.crypto import get_random_string
import requests


from accounts.jwt_utils import generate_jwt, verify_jwt
from accounts.models import UserProfile

def get_authenticated_admin(request):
    """
    Helper to verify request's JWT token and check if they are an administrator.
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise Exception('Authentication credentials were not provided')
    token = auth_header.split(' ')[1]
    payload = verify_jwt(token)
    user_id = payload.get('user_id')
    user = User.objects.get(id=user_id)
    if not user.is_superuser:
        raise Exception('Permission denied: Administrator role required')
    return user

@csrf_exempt
def register_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        name = data.get('name', '')
        
        if not email or not password:
            return JsonResponse({'error': 'Email and password are required'}, status=400)
            
        # Check if email/username already exists
        if User.objects.filter(username=email).exists():
            return JsonResponse({'error': 'An account with this email already exists'}, status=400)
            
        # Create standard Django user
        first_name = name.split(' ')[0] if name else ''
        last_name = ' '.join(name.split(' ')[1:]) if name and len(name.split(' ')) > 1 else ''
        
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        user.save()
        
        # Get role
        role = user.profile.role if hasattr(user, 'profile') else 'Creator'
        
        # Generate JWT token
        token = generate_jwt(user)
        
        return JsonResponse({
            'message': 'Registration successful',
            'token': token,
            'user': {
                'email': user.email,
                'name': name,
                'role': role
            }
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def login_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
        
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return JsonResponse({'error': 'Email and password are required'}, status=400)
            
        # Authenticate user (Django uses username for auth, which we set to email)
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            name = f"{user.first_name} {user.last_name}".strip() or user.username
            role = user.profile.role if hasattr(user, 'profile') else ('Administrator' if user.is_superuser else 'Creator')
            token = generate_jwt(user)
            return JsonResponse({
                'message': 'Login successful',
                'token': token,
                'user': {
                    'email': user.email,
                    'name': name,
                    'role': role
                }
            })
        else:
            return JsonResponse({'error': 'Invalid email or password'}, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def google_login_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
        
    try:
        data = json.loads(request.body)
        token = data.get('credential')
        
        if not token:
            return JsonResponse({'error': 'Google credential token is required'}, status=400)
            
        # Get Google Client ID from environment variables
        google_client_id = os.getenv('GOOGLE_CLIENT_ID')
        
        try:
            # Verify the Google ID Token
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), google_client_id)
            
            email = idinfo.get('email')
            name = idinfo.get('name', '')
            
            if not email:
                return JsonResponse({'error': 'Could not extract email from Google identity token'}, status=400)
                
            # Find or create user
            try:
                user = User.objects.get(username=email)
            except User.DoesNotExist:
                first_name = name.split(' ')[0] if name else ''
                last_name = ' '.join(name.split(' ')[1:]) if name and len(name.split(' ')) > 1 else ''
                
                # Google accounts login with OAuth, create a random local password
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=get_random_string(32),
                    first_name=first_name,
                    last_name=last_name
                )
                user.save()
                
            # Generate JWT token
            local_token = generate_jwt(user)
            role = user.profile.role if hasattr(user, 'profile') else ('Administrator' if user.is_superuser else 'Creator')
            
            user_display_name = f"{user.first_name} {user.last_name}".strip() or user.username
            return JsonResponse({
                'message': 'Google authentication successful',
                'token': local_token,
                'user': {
                    'email': user.email,
                    'name': user_display_name,
                    'role': role
                }
            })
            
        except ValueError as ve:
            return JsonResponse({'error': f'Invalid Google token: {str(ve)}'}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def list_users_view(request):
    """
    API for administrators to retrieve all users in the system.
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET method is allowed'}, status=405)
        
    try:
        # Check permissions
        get_authenticated_admin(request)
        
        users_list = []
        for u in User.objects.all().order_by('id'):
            role = u.profile.role if hasattr(u, 'profile') else ('Administrator' if u.is_superuser else 'Creator')
            display_name = f"{u.first_name} {u.last_name}".strip() or u.username
            users_list.append({
                'id': u.id,
                'email': u.email,
                'name': display_name,
                'role': role
            })
            
        return JsonResponse({'users': users_list})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=403 if 'Permission denied' in str(e) or 'credentials' in str(e) else 500)

@csrf_exempt
def update_user_role_view(request):
    """
    API for administrators to update any user's role.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
        
    try:
        # Check permissions
        get_authenticated_admin(request)
        
        data = json.loads(request.body)
        user_id = data.get('userId')
        new_role = data.get('role')
        
        if not user_id or not new_role:
            return JsonResponse({'error': 'userId and role are required'}, status=400)
            
        # Get target user
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
            
        # Update user profile
        profile, created = UserProfile.objects.get_or_create(user=target_user)
        profile.role = new_role
        profile.save()
        
        # Keep superuser status in sync if they are made administrator or demoted
        if new_role == 'Administrator':
            target_user.is_superuser = True
            target_user.is_staff = True
        else:
            target_user.is_superuser = False
            target_user.is_staff = False
        target_user.save()
        
        return JsonResponse({'message': 'User role updated successfully', 'userId': user_id, 'role': new_role})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=403 if 'Permission denied' in str(e) or 'credentials' in str(e) else 500)

def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'CreatorIQ Django API'})

@csrf_exempt
def youtube_channel_analytics(request):
    """
    Fetches live statistics and recent videos for a YouTube channel.
    Accepts query parameter:
      q: channel name/handle search query, OR
      channel_id: exact YouTube channel ID.
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET method is allowed'}, status=405)

    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        return JsonResponse({'error': 'YouTube API Key is not configured on the backend.'}, status=500)

    q = request.GET.get('q', '').strip()
    channel_id = request.GET.get('channel_id', '').strip()

    if not q and not channel_id:
        return JsonResponse({'error': 'Either "q" or "channel_id" parameter is required.'}, status=400)

    try:
        # Step 1: If q is provided and not channel_id, search for the channel ID
        if q and not channel_id:
            search_url = 'https://www.googleapis.com/youtube/v3/search'
            search_params = {
                'part': 'snippet',
                'type': 'channel',
                'q': q,
                'maxResults': 1,
                'key': api_key
            }
            res = requests.get(search_url, params=search_params, timeout=5)
            if res.status_code != 200:
                return JsonResponse({'error': f'YouTube search API error: {res.text}'}, status=res.status_code)
            
            search_data = res.json()
            items = search_data.get('items', [])
            if not items:
                return JsonResponse({'error': f'No channel found matching "{q}"'}, status=404)
            
            channel_id = items[0]['id']['channelId']

        # Step 2: Fetch channel details and stats
        channel_url = 'https://www.googleapis.com/youtube/v3/channels'
        channel_params = {
            'part': 'snippet,statistics,brandingSettings',
            'id': channel_id,
            'key': api_key
        }
        res = requests.get(channel_url, params=channel_params, timeout=5)
        if res.status_code != 200:
            return JsonResponse({'error': f'YouTube channels API error: {res.text}'}, status=res.status_code)

        channel_data = res.json()
        channel_items = channel_data.get('items', [])
        if not channel_items:
            return JsonResponse({'error': 'Channel details not found.'}, status=404)

        channel_item = channel_items[0]
        snippet = channel_item.get('snippet', {})
        stats = channel_item.get('statistics', {})
        branding = channel_item.get('brandingSettings', {})
        
        channel_info = {
            'id': channel_id,
            'title': snippet.get('title', ''),
            'handle': snippet.get('customUrl', ''),
            'description': snippet.get('description', ''),
            'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
            'banner': branding.get('image', {}).get('bannerExternalUrl', ''),
            'subscribers': int(stats.get('subscriberCount', 0)),
            'views': int(stats.get('viewCount', 0)),
            'videos': int(stats.get('videoCount', 0)),
        }

        # Step 3: Fetch 5 recent videos
        videos_search_url = 'https://www.googleapis.com/youtube/v3/search'
        videos_search_params = {
            'part': 'snippet',
            'channelId': channel_id,
            'order': 'date',
            'type': 'video',
            'maxResults': 5,
            'key': api_key
        }
        res = requests.get(videos_search_url, params=videos_search_params, timeout=5)
        recent_videos = []
        
        if res.status_code == 200:
            video_items = res.json().get('items', [])
            video_ids = [item['id']['videoId'] for item in video_items if item.get('id', {}).get('videoId')]
            
            if video_ids:
                # Step 4: Fetch detailed video statistics
                videos_url = 'https://www.googleapis.com/youtube/v3/videos'
                videos_params = {
                    'part': 'snippet,statistics',
                    'id': ','.join(video_ids),
                    'key': api_key
                }
                v_res = requests.get(videos_url, params=videos_params, timeout=5)
                if v_res.status_code == 200:
                    v_items = v_res.json().get('items', [])
                    v_stats_map = {item['id']: item for item in v_items}
                    
                    for v_id in video_ids:
                        if v_id in v_stats_map:
                            v_item = v_stats_map[v_id]
                            v_snippet = v_item.get('snippet', {})
                            v_stats = v_item.get('statistics', {})
                            recent_videos.append({
                                'id': v_id,
                                'title': v_snippet.get('title', ''),
                                'publishedAt': v_snippet.get('publishedAt', ''),
                                'thumbnail': v_snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                                'views': int(v_stats.get('viewCount', 0)),
                                'likes': int(v_stats.get('likeCount', 0)),
                                'comments': int(v_stats.get('commentCount', 0))
                            })

        return JsonResponse({
            'channel': channel_info,
            'videos': recent_videos
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

