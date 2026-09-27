import requests
from bs4 import BeautifulSoup
from flask import current_app

def fetch_metadata(url):
    """
    Safely fetches metadata (title and description) from a URL.
    Returns a dictionary: {'title': ..., 'description': ...}
    """
    metadata = {'title': '', 'description': ''}
    
    try:
        # Use a timeout from config or default to 5 seconds
        timeout = current_app.config.get('REQUEST_TIMEOUT', 5)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/112.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        if soup.title and soup.title.string:
            metadata['title'] = soup.title.string.strip()
            
        # Extract description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            metadata['description'] = meta_desc['content'].strip()
        else:
            # Fallback to og:description
            og_desc = soup.find('meta', property='og:description')
            if og_desc and og_desc.get('content'):
                metadata['description'] = og_desc['content'].strip()
                
    except Exception as e:
        # We silently fail on metadata fetch and let the user manually enter it
        current_app.logger.warning(f"Failed to fetch metadata for {url}: {str(e)}")
        
    return metadata
