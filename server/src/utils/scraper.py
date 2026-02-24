import trafilatura

def scrape_url(url: str) -> str:
    """
    Fetches a webpage and extracts clean, readable main article content.
    Uses Trafilatura to automatically strip out navigation, headers, footers, 
    ads, and scripts, ensuring high-quality data for the RAG engine.
    """
    print(f"Scraping: {url}")
    
    try:
        # --- 1. FETCH HTML ---
        # Trafilatura handles headers, timeouts, and redirects automatically
        downloaded = trafilatura.fetch_url(url)
        
        if downloaded is None:
            print(f"Scraping Failed: Could not download data from {url}")
            return ""

        # --- 2. EXTRACT MAIN CONTENT ---
        # include_comments=False ensures we don't get messy forum replies at the bottom of articles
        clean_text = trafilatura.extract(downloaded, include_comments=False, include_tables=True)

        if clean_text:
            return clean_text[:20000] 
        else:
            print(f"Scraping Warning: No main readable content found at {url}")
            return ""
            
    except Exception as e:
        print(f"Scraping Error: {e}")
        return ""