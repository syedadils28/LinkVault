import os
from datetime import datetime
from flask import current_app
from app.exporters.docx_exporter import export_docx
from app.exporters.excel_exporter import export_excel
from app.exporters.markdown_exporter import export_markdown
from app.exporters.csv_exporter import export_csv
from app.exporters.json_exporter import export_json
from app.exporters.pdf_exporter import export_pdf

def generate_export(links, format_type, collection_name=None):
    """
    Orchestrates the export process based on the requested format.
    Returns the file path to the generated export.
    """
    export_dir = current_app.config['EXPORT_DIR']
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_name = "LinkVault_Export"
    if collection_name:
        safe_name = "".join([c if c.isalnum() else "_" for c in collection_name])
        
    filename = f"{safe_name}_{timestamp}.{format_type}"
    filepath = os.path.join(export_dir, filename)
    
    if format_type == 'docx':
        return export_docx(links, collection_name, filepath)
    elif format_type == 'xlsx':
        return export_excel(links, filepath)
    elif format_type == 'md':
        return export_markdown(links, collection_name, filepath)
    elif format_type == 'csv':
        return export_csv(links, filepath)
    elif format_type == 'json':
        return export_json(links, collection_name, filepath)
    elif format_type == 'pdf':
        return export_pdf(links, collection_name, filepath)
    else:
        raise ValueError(f"Unsupported format: {format_type}")
