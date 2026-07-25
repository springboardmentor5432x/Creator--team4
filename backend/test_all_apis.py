import os
import sys
import json
import django

# Setup Django environment
os.environ['ALLOWED_HOSTS'] = 'localhost,127.0.0.1,testserver'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from accounts.jwt_utils import generate_jwt

def run_tests():
    print("--- Starting API Checks ---")
    client = Client()
    
    # Create or get a test user
    user, created = User.objects.get_or_create(username='testuser', email='test@example.com')
    if created:
        user.set_password('password123')
        user.save()
        
    token = generate_jwt(user)
    headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
    
    endpoints = [
        ('GET', '/api/me/', {}),
        ('POST', '/api/users/connect-instagram/', {'username': 'testig'}),
        ('GET', '/api/instagram/analytics/', {}),
        ('POST', '/api/users/connect-facebook/', {'pageName': 'Code Hub', 'groupId': '1571965316444595'}),
        ('GET', '/api/facebook/analytics/', {}),
        ('POST', '/api/users/connect-twitter/', {'username': 'narendramodi'}),
        ('GET', '/api/twitter/analytics/', {}),
        ('POST', '/api/users/connect-youtube/', {'channelId': 'UC_x5XG1OV2P6uZZ5FSM9Ttw'}),
        ('GET', '/api/youtube/analytics/', {}),
        ('POST', '/api/users/connect-linkedin/', {'profileUrl': 'https://linkedin.com/in/test'}),
        ('GET', '/api/linkedin/analytics/', {}),
        ('GET', '/api/workflows/', {}),
    ]

    for method, url, data in endpoints:
        print(f"Testing {method} {url} ... ", end="")
        try:
            if method == 'GET':
                response = client.get(url, content_type='application/json', **headers)
            else:
                response = client.post(url, data=json.dumps(data), content_type='application/json', **headers)
            
            if response.status_code in [200, 201]:
                print(f"OK ({response.status_code})")
            else:
                print(f"FAILED ({response.status_code}) - {response.content[:100]}")
        except Exception as e:
            print(f"ERROR: {e}")

    print("--- API Checks Completed ---")

if __name__ == '__main__':
    run_tests()
