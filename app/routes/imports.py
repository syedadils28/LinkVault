import json
import csv
from io import StringIO
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.link import Link
from app.services.link_service import detect_link_type

imports_bp = Blueprint('imports', __name__)

@imports_bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_links():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
            
        if file:
            filename = file.filename.lower()
            try:
                content = file.read().decode('utf-8')
                imported_count = 0
                
                if filename.endswith('.json'):
                    data = json.loads(content)
                    links = data.get('links', [])
                    for link_data in links:
                        url = link_data.get('url')
                        if not url:
                            continue
                            
                        # Basic duplicate check
                        if not Link.query.filter_by(user_id=current_user.id, url=url).first():
                            link = Link(
                                url=url,
                                title=link_data.get('title', ''),
                                description=link_data.get('description', ''),
                                link_type=link_data.get('type') or detect_link_type(url),
                                is_favorite=link_data.get('favorite', False),
                                user_id=current_user.id
                            )
                            db.session.add(link)
                            imported_count += 1
                            
                elif filename.endswith('.csv'):
                    reader = csv.DictReader(StringIO(content))
                    for row in reader:
                        url = row.get('URL')
                        if not url:
                            continue
                            
                        if not Link.query.filter_by(user_id=current_user.id, url=url).first():
                            link = Link(
                                url=url,
                                title=row.get('Title', ''),
                                description=row.get('Description', ''),
                                link_type=row.get('Type') or detect_link_type(url),
                                is_favorite=row.get('Favorite', '').lower() == 'yes',
                                user_id=current_user.id
                            )
                            db.session.add(link)
                            imported_count += 1
                else:
                    flash('Unsupported file format. Please use JSON or CSV.', 'error')
                    return redirect(request.url)
                    
                db.session.commit()
                flash(f'Successfully imported {imported_count} links.', 'success')
                return redirect(url_for('dashboard.index'))
                
            except Exception as e:
                flash(f'Error parsing file: {str(e)}', 'error')
                return redirect(request.url)
                
    return render_template('import.html')
