import requests
from bs4 import BeautifulSoup
import re

def scrape_url(url: str) -> str:
    """
    Fetches a URL and returns clean, readable text.
    """
    print(f"🕷️ Scraping: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Kill script and style elements
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.extract()    

        # 2. Get text
        text = soup.get_text()

        # 3. Clean whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return clean_text[:20000] 
        
    except Exception as e:
        print(f"❌ Scraping Failed: {e}")
        return ""