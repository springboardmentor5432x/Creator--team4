import urllib.request
import json
import os
from dotenv import load_dotenv

load_dotenv()

access_token = os.getenv('META_API_KEY')
app_id = os.getenv('META_APP_ID')

print(f"Testing Instagram API for user 'biswajiit00'...")

# 1. Fetch User Profile Details
url_profile = f"https://graph.instagram.com/v19.0/me?fields=id,username,account_type,media_count&access_token={access_token}"

try:
    print("\n--- GET /v19.0/me ---")
    req = urllib.request.Request(url_profile)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        print("Status: 200 OK")
        print(f"User ID: {data.get('id')}")
        print(f"Username: @{data.get('username')}")
        print(f"Account Type: {data.get('account_type')}")
        print(f"Total Media Count: {data.get('media_count')}")
except Exception as e:
    print(f"Error fetching profile: {e}")

# 2. Fetch User Media Feed
url_media = f"https://graph.instagram.com/v19.0/me/media?fields=id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count&access_token={access_token}"

try:
    print("\n--- GET /v19.0/me/media ---")
    req = urllib.request.Request(url_media)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        print("Status: 200 OK")
        print(f"Total Posts Returned: {len(data.get('data', []))}")
        print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error fetching media feed: {e}")

# 3. Test Container Creation (POST request validation)
url_create_container = f"https://graph.instagram.com/v19.0/27380985381597260/media"
post_data = urllib.parse.urlencode({
    'image_url': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800',
    'caption': 'Test post from CreatorIQ Analytics Dashboard 🚀 #CreatorIQ #InstagramAPI',
    'access_token': access_token
}).encode('utf-8')

try:
    print("\n--- POST /v19.0/{ig-user-id}/media (Container Creation Validation) ---")
    req = urllib.request.Request(url_create_container, data=post_data, method='POST')
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        print("Status: 200 OK - POST Request Validated Successfully!")
        print(f"Created Container ID: {data.get('id')}")
except urllib.error.HTTPError as e:
    err_body = e.read().decode('utf-8')
    print(f"POST Request HTTPError {e.code}: {err_body}")
except Exception as e:
    print(f"Error: {e}")
