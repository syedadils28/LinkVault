import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required, current_user
from app.models.link import Link
from app.models.collection import Collection
from app.services.export_service import generate_export

exports_bp = Blueprint('exports', __name__)

@exports_bp.route('/export', methods=['GET', 'POST'])
@login_required
def export_links():
    collections = Collection.query.filter_by(user_id=current_user.id).all()
    
    if request.method == 'POST':
        format_type = request.form.get('format')
        scope = request.form.get('scope') # 'all', 'collection', 'selected'
        
        links = []
        collection_name = None
        
        if scope == 'all':
            links = Link.query.filter_by(user_id=current_user.id).all()
        elif scope == 'collection':
            collection_id = request.form.get('collection_id')
            collection = Collection.query.filter_by(id=collection_id, user_id=current_user.id).first()
            if collection:
                links = collection.links.all()
                collection_name = collection.name
        elif scope == 'selected':
            # Handle selected IDs (comma separated)
            selected_ids = request.form.get('selected_ids', '')
            if selected_ids:
                ids = [int(i) for i in selected_ids.split(',')]
                links = Link.query.filter(Link.id.in_(ids), Link.user_id == current_user.id).all()
                
        if not links:
            flash('No links found for the selected criteria.', 'warning')
            return redirect(url_for('exports.export_links'))
            
        try:
            filepath = generate_export(links, format_type, collection_name)
            filename = os.path.basename(filepath)
            
            return send_file(
                filepath,
                as_attachment=True,
                download_name=filename
            )
        except Exception as e:
            current_app.logger.error(f"Export error: {str(e)}")
            flash(f'An error occurred during export: {str(e)}', 'error')
            return redirect(url_for('exports.export_links'))
            
    return render_template('export.html', collections=collections)
