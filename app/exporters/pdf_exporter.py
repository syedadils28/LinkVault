from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
import datetime

def export_pdf(links, collection_name, filepath):
    """
    Exports a list of links to a PDF document using ReportLab.
    """
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    Story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Heading2'], alignment=TA_CENTER)
    link_title_style = styles['Heading3']
    normal_style = styles['Normal']
    url_style = ParagraphStyle('URL', parent=styles['Normal'], textColor=colors.blue)
    meta_style = ParagraphStyle('Meta', parent=styles['Normal'], textColor=colors.grey)
    
    # Title
    Story.append(Paragraph("LINKVAULT", title_style))
    subtitle_text = f"Collection: {collection_name}" if collection_name else "Saved Links"
    Story.append(Paragraph(subtitle_text, subtitle_style))
    Story.append(Paragraph(f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d')}", meta_style))
    Story.append(Spacer(1, 24))
    
    for i, link in enumerate(links, 1):
        # Link Title
        Story.append(Paragraph(f"{i}. {link.title or 'Untitled Link'}", link_title_style))
        Story.append(Spacer(1, 6))
        
        # URL
        Story.append(Paragraph(f"<b>URL:</b> <a href='{link.url}'>{link.url}</a>", url_style))
        Story.append(Spacer(1, 6))
        
        # Metadata
        col_text = link.collection.name if link.collection else "None"
        tag_text = ", ".join(tag.name for tag in link.tags) if link.tags else "None"
        meta_info = f"<b>Type:</b> {link.link_type} | <b>Collection:</b> {col_text} | <b>Tags:</b> {tag_text}"
        Story.append(Paragraph(meta_info, normal_style))
        Story.append(Spacer(1, 6))
        
        # Description
        if link.description:
            Story.append(Paragraph("<b>Description:</b>", normal_style))
            Story.append(Paragraph(link.description.replace('\n', '<br/>'), normal_style))
            
        Story.append(Spacer(1, 12))
        Story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey, spaceBefore=1, spaceAfter=1, hAlign='CENTER'))
        Story.append(Spacer(1, 12))
        
    doc.build(Story)
    return filepath
