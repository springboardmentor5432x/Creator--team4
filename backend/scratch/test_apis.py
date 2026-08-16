import os
import requests
from dotenv import load_dotenv

load_dotenv('.env')

print("--- 1. Testing Instagram RapidAPI ---")
rapidapi_key = os.getenv('RAPIDAPI_KEY')
rapidapi_host = os.getenv('RAPIDAPI_IG_HOST', 'instagram120.p.rapidapi.com')
print(f"Key: {rapidapi_key[:10]}... Host: {rapidapi_host}")

try:
    url = f"https://{rapidapi_host}/api/instagram/profile"
    headers = {
        'Content-Type': 'application/json',
        'x-rapidapi-host': rapidapi_host,
        'x-rapidapi-key': rapidapi_key
    }
    r = requests.post(url, json={'username': 'leomessi'}, headers=headers, timeout=10)
    print("IG Status:", r.status_code)
    print("IG Response:", r.text[:300])
except Exception as e:
    print("IG Error:", e)

print("\n--- 2. Testing Facebook scraping ---")
try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    r_fb = requests.get('https://www.facebook.com/cristiano', headers=headers, timeout=10)
    print("FB Status:", r_fb.status_code)
    print("FB HTML length:", len(r_fb.text))
except Exception as e:
    print("FB Error:", e)

print("\n--- 3. Checking LinkedIn config ---")
li_id = os.getenv('LINKEDIN_CLIENT_ID')
li_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
print(f"LinkedIn Client ID: {li_id}")
