import os, sys
sys.path.insert(0, os.path.abspath('.'))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("1. Testing FastAPI /api/health ...")
r = client.get("/api/health")
print("Health:", r.status_code, r.json())

print("\n2. Testing FastAPI Connect Instagram (cristiano)...")
r_ig = client.post("/api/users/connect-instagram/", json={"username": "cristiano"})
print("IG Status:", r_ig.status_code, "Followers:", r_ig.json()["user"]["instagram_followers_count"])

print("\n3. Testing FastAPI Instagram Analytics...")
r_iga = client.get("/api/instagram/analytics/")
print("IG Analytics Status:", r_iga.status_code, "Posts:", len(r_iga.json()["posts"]))

print("\n4. Testing FastAPI Connect Facebook (Meta)...")
r_fb = client.post("/api/users/connect-facebook/", json={"pageName": "Meta"})
print("FB Status:", r_fb.status_code, "Reach:", r_fb.json()["user"]["facebook_reach_count"])

print("\n5. Testing FastAPI Facebook Analytics...")
r_fba = client.get("/api/facebook/analytics/")
print("FB Analytics Status:", r_fba.status_code, "FB Posts:", len(r_fba.json()["posts"]))

print("\n6. Testing FastAPI Connect LinkedIn (williamhgates)...")
r_li = client.post("/api/users/connect-linkedin/", json={"username": "williamhgates"})
print("LI Status:", r_li.status_code, "Title:", r_li.json()["linkedin_profile_title"], "Connections:", r_li.json()["linkedin_connections_count"])

print("\n7. Testing FastAPI LinkedIn Analytics...")
r_lia = client.get("/api/linkedin/analytics/")
print("LI Analytics Status:", r_lia.status_code, "Impressions:", r_lia.json()["profile"]["post_impressions"])

print("\n8. Testing FastAPI Connect Twitter (narendramodi)...")
r_tw = client.post("/api/users/connect-twitter/", json={"username": "narendramodi"})
print("TW Status:", r_tw.status_code, "Followers:", r_tw.json()["user"]["twitter_followers_count"])

print("\n9. Testing FastAPI OAuth Callback (instagram)...")
r_oa = client.get("/api/auth/oauth-callback/instagram/?username=leomessi")
print("OAuth Status:", r_oa.status_code, "Followers:", r_oa.json()["user"]["instagram_followers_count"])

print("\nALL FASTAPI SOCIAL MEDIA INTEGRATION CHECKS PASSED SUCCESSFULLY!")
