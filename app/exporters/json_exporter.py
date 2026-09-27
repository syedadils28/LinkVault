import json

def export_json(links, collection_name, filepath):
    """
    Exports a list of links to a structured JSON file.
    """
    output = {
        "collection": collection_name or "All Links",
        "description": f"Exported from LinkVault" if collection_name else "All saved links",
        "links": [link.to_dict() for link in links]
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        
    return filepath
