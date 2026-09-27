import re
from urllib.parse import urlparse
from app.models.link import Link

def detect_link_type(url):
    """
    Detects the link type based on the URL domain.
    """
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Strip www.
        if domain.startswith('www.'):
            domain = domain[4:]
            
        if 'github.com' in domain:
            return 'GitHub'
        elif 'youtube.com' in domain or 'youtu.be' in domain:
            return 'YouTube'
        elif 'docs.python.org' in domain or 'readthedocs.io' in domain or 'docs.' in domain:
            return 'Documentation'
        elif 'arxiv.org' in domain or 'researchgate.net' in domain:
            return 'Research Paper'
        elif 'medium.com' in domain or 'dev.to' in domain or 'hashnode.dev' in domain:
            return 'Article'
        elif 'stackoverflow.com' in domain:
            return 'Development Tool'
        elif 'coursera.org' in domain or 'udemy.com' in domain:
            return 'Course'
            
        return 'Website'
    except Exception:
        return 'Website'

def check_duplicate(user_id, url):
    """
    Checks if the user already has this exact URL saved.
    Returns the existing Link object if found, else None.
    """
    # Simple normalizer: remove trailing slashes
    normalized_url = url.rstrip('/')
    
    # We could do more complex normalization, but let's stick to exact match and no-slash match
    existing_link = Link.query.filter_by(user_id=user_id, url=url).first()
    if not existing_link:
        existing_link = Link.query.filter_by(user_id=user_id, url=normalized_url).first()
        
    return existing_link
