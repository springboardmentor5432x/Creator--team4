import os, re, json, requests
from bs4 import BeautifulSoup

def test_instagram_scraping(username):
    print(f"\n--- Testing Instagram Scraping for @{username} ---")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    # 1. Try public profile page meta tags
    try:
        url = f"https://www.instagram.com/{username}/"
        r = requests.get(url, headers=headers, timeout=8)
        print("IG Web page status:", r.status_code)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            # Look for meta description: e.g. "494M Followers, 308 Following, 1,234 Posts - See Instagram photos and videos from Leo Messi (@leomessi)"
            meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
            if meta_desc and meta_desc.get('content'):
                desc = meta_desc['content']
                print("IG Meta desc:", desc)
                m = re.search(r'([0-9,.]+[KMkm]?)\s*Followers,\s*([0-9,.]+[KMkm]?)\s*Following,\s*([0-9,.]+[KMkm]?)\s*Posts', desc)
                if m:
                    print("Found stats via meta tags:", m.groups())
            og_image = soup.find('meta', attrs={'property': 'og:image'})
            if og_image:
                print("Found profile pic:", og_image.get('content')[:60])
    except Exception as e:
        print("IG scrape error:", e)

def test_facebook_scraping(page_name):
    print(f"\n--- Testing Facebook Scraping for {page_name} ---")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    try:
        url = f"https://m.facebook.com/{page_name}"
        r = requests.get(url, headers=headers, timeout=8)
        print("FB mobile page status:", r.status_code)
        soup = BeautifulSoup(r.text, 'html.parser')
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        og_image = soup.find('meta', attrs={'property': 'og:image'})
        print("FB Title:", og_title.get('content') if og_title else None)
        print("FB Desc:", og_desc.get('content') if og_desc else None)
        print("FB Image:", og_image.get('content')[:60] if og_image else None)
    except Exception as e:
        print("FB scrape error:", e)

def test_linkedin_scraping(username):
    print(f"\n--- Testing LinkedIn Public Scraping for {username} ---")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    try:
        url = f"https://www.linkedin.com/in/{username}"
        r = requests.get(url, headers=headers, timeout=8)
        print("LI page status:", r.status_code)
        soup = BeautifulSoup(r.text, 'html.parser')
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        og_image = soup.find('meta', attrs={'property': 'og:image'})
        print("LI Title:", og_title.get('content') if og_title else None)
        print("LI Desc:", og_desc.get('content') if og_desc else None)
        print("LI Image:", og_image.get('content')[:60] if og_image else None)
    except Exception as e:
        print("LI scrape error:", e)

test_instagram_scraping('instagram')
test_facebook_scraping('Meta')
test_linkedin_scraping('williamhgates')
