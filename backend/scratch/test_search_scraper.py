import requests, re
from bs4 import BeautifulSoup

def search_instagram_stats(username):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
    url = f"https://html.duckduckgo.com/html/?q=site:instagram.com/{username}+followers"
    try:
        r = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(r.text, 'html.parser')
        snippets = soup.find_all('a', class_='result__snippet')
        for s in snippets:
            text = s.get_text()
            print("DDG Snippet:", text)
            m = re.search(r'([\d,.]+[MKkm]?)\s*Followers.*?([\d,.]+[MKkm]?)\s*Following.*?([\d,.]+[MKkm]?)\s*Posts', text, re.IGNORECASE)
            if m:
                print("DDG Extracted Stats:", m.groups())
                return m.groups()
    except Exception as e:
        print("Search error:", e)
    return None

def search_facebook_stats(page_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
    url = f"https://html.duckduckgo.com/html/?q=site:facebook.com/{page_name}+followers+likes"
    try:
        r = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(r.text, 'html.parser')
        snippets = soup.find_all('a', class_='result__snippet')
        for s in snippets:
            text = s.get_text()
            print("FB Snippet:", text)
            m_fol = re.search(r'([\d,.]+[MKkm]?)\s*followers', text, re.IGNORECASE)
            m_likes = re.search(r'([\d,.]+[MKkm]?)\s*likes', text, re.IGNORECASE)
            if m_fol or m_likes:
                print("FB Extracted:", m_fol.group(1) if m_fol else None, m_likes.group(1) if m_likes else None)
    except Exception as e:
        print("FB search error:", e)

print("--- Testing DuckDuckGo for Instagram ---")
search_instagram_stats('cristiano')
print("\n--- Testing DuckDuckGo for Facebook ---")
search_facebook_stats('cristiano')
