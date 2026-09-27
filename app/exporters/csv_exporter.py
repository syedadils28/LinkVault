import pandas as pd

def export_csv(links, filepath):
    """
    Exports a list of links to a CSV file.
    """
    data = []
    for link in links:
        data.append({
            'Title': link.title or '',
            'URL': link.url,
            'Description': link.description or '',
            'Type': link.link_type or '',
            'Collection': link.collection.name if link.collection else '',
            'Tags': ', '.join(tag.name for tag in link.tags),
            'Favorite': 'Yes' if link.is_favorite else 'No',
            'Created Date': link.created_at.strftime('%Y-%m-%d %H:%M:%S') if link.created_at else ''
        })
        
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)
    
    return filepath
