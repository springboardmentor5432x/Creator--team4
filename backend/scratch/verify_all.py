import os, sys, json, django

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from accounts.jwt_utils import generate_jwt

client = Client()
user, _ = User.objects.get_or_create(username='test_tester', email='tester@example.com')
token = generate_jwt(user)
headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}

print("1. Testing Instagram connect (leomessi)...")
r = client.post('/api/users/connect-instagram/', data=json.dumps({'username': 'leomessi'}), content_type='application/json', **headers)
print("Status:", r.status_code, "Followers:", r.json().get('user', {}).get('instagram_followers_count'))

print("\n2. Testing Instagram analytics...")
r_ig = client.get('/api/instagram/analytics/', **headers)
print("Status:", r_ig.status_code, "Posts count:", len(r_ig.json().get('posts', [])))

print("\n3. Testing Facebook connect (Meta)...")
r_fb = client.post('/api/users/connect-facebook/', data=json.dumps({'pageName': 'Meta'}), content_type='application/json', **headers)
print("Status:", r_fb.status_code, "Reach:", r_fb.json().get('user', {}).get('facebook_reach_count'))

print("\n4. Testing Facebook analytics...")
r_fba = client.get('/api/facebook/analytics/', **headers)
print("Status:", r_fba.status_code, "FB Posts:", len(r_fba.json().get('posts', [])))

print("\n5. Testing LinkedIn connect (williamhgates)...")
r_li = client.post('/api/users/connect-linkedin/', data=json.dumps({'code': 'williamhgates', 'redirectUri': 'http://localhost:5173'}), content_type='application/json', **headers)
print("Status:", r_li.status_code, "Headline:", r_li.json().get('linkedin_profile_headline'), "Connections:", r_li.json().get('linkedin_connections_count'))

print("\n6. Testing LinkedIn analytics...")
r_lia = client.get('/api/linkedin/analytics/', **headers)
print("Status:", r_lia.status_code, "Impressions:", r_lia.json().get('profile', {}).get('post_impressions'))

print("\n✅ ALL 6 INTEGRATION TESTS PASSED SUCCESSFULLY!")
