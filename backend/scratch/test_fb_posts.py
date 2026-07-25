import requests, re, json
url = 'https://www.facebook.com/narendramodi/'
FB_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
}
r = requests.get(url, headers=FB_HEADERS, timeout=20)
print('Len:', len(r.text))

# Save the full HTML for manual inspection if needed
with open('c:/infosys/creator_iq/backend/scratch/fb_output.html', 'w', encoding='utf-8') as f:
    f.write(r.text)

# We can search for '"story":{"message":{"text":' or similar structures in the HTML
# Facebook uses GraphQL responses in script tags. 
# We'll look for timeline/feed data in the script tags.
print("Check fb_output.html for full HTML.")
