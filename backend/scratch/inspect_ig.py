import requests, re
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}
r = requests.get('https://www.instagram.com/cristiano/', headers=headers, timeout=8)
print("Status:", r.status_code)
soup = BeautifulSoup(r.text, 'html.parser')
for meta in soup.find_all('meta'):
    prop = meta.get('property') or meta.get('name')
    content = meta.get('content')
    if prop and content:
        print(f"{prop}: {content[:100]}")
