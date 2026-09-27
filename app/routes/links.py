from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.link import Link
from app.models.collection import Collection
from app.models.tag import Tag
from app.services.metadata_service import fetch_metadata
from app.services.link_service import detect_link_type, check_duplicate

links_bp = Blueprint('links', __name__)

@links_bp.route('/links')
@login_required
def view_links():
    links = Link.query.filter_by(user_id=current_user.id).order_by(Link.created_at.desc()).all()
    collections = Collection.query.filter_by(user_id=current_user.id).all()
    return render_template('links.html', links=links, collections=collections)

@links_bp.route('/links/add', methods=['GET', 'POST'])
@login_required
def add_link():
    collections = Collection.query.filter_by(user_id=current_user.id).all()
    
    if request.method == 'POST':
        url = request.form.get('url')
        
        # Check duplicate
        duplicate = check_duplicate(current_user.id, url)
        if duplicate and request.form.get('ignore_duplicate') != 'true':
            return render_template('add_link.html', collections=collections, url=url, duplicate=duplicate)
            
        title = request.form.get('title')
        description = request.form.get('description')
        collection_id = request.form.get('collection_id')
        link_type = request.form.get('link_type') or detect_link_type(url)
        is_favorite = 'is_favorite' in request.form
        notes = request.form.get('notes')
        tags_input = request.form.get('tags', '')
        
        # Process tags
        tag_objects = []
        if tags_input:
            tag_names = [t.strip().lower() for t in tags_input.split(',')]
            for name in tag_names:
                if name:
                    tag = Tag.query.filter_by(name=name, user_id=current_user.id).first()
                    if not tag:
                        tag = Tag(name=name, user_id=current_user.id)
                        db.session.add(tag)
                    tag_objects.append(tag)
                    
        link = Link(
            url=url,
            title=title,
            description=description,
            link_type=link_type,
            is_favorite=is_favorite,
            notes=notes,
            user_id=current_user.id,
            collection_id=collection_id if collection_id else None,
            tags=tag_objects
        )
        
        db.session.add(link)
        db.session.commit()
        flash('Link added successfully', 'success')
        return redirect(url_for('links.view_links'))
        
    url = request.args.get('url', '')
    title = request.args.get('title', '')
    return render_template('add_link.html', collections=collections, url=url, title=title)

@links_bp.route('/api/fetch-metadata', methods=['POST'])
@login_required
def api_fetch_metadata():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400
        
    metadata = fetch_metadata(url)
    link_type = detect_link_type(url)
    
    return jsonify({
        'title': metadata.get('title', ''),
        'description': metadata.get('description', ''),
        'link_type': link_type
    })

@links_bp.route('/links/<int:link_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_link(link_id):
    link = Link.query.filter_by(id=link_id, user_id=current_user.id).first_or_404()
    collections = Collection.query.filter_by(user_id=current_user.id).all()
    
    if request.method == 'POST':
        link.title = request.form.get('title')
        link.url = request.form.get('url')
        link.description = request.form.get('description')
        link.notes = request.form.get('notes')
        link.link_type = request.form.get('link_type')
        link.is_favorite = 'is_favorite' in request.form
        
        col_id = request.form.get('collection_id')
        link.collection_id = col_id if col_id else None
        
        tags_input = request.form.get('tags', '')
        tag_objects = []
        if tags_input:
            tag_names = [t.strip().lower() for t in tags_input.split(',')]
            for name in tag_names:
                if name:
                    tag = Tag.query.filter_by(name=name, user_id=current_user.id).first()
                    if not tag:
                        tag = Tag(name=name, user_id=current_user.id)
                        db.session.add(tag)
                    tag_objects.append(tag)
                    
        link.tags = tag_objects
        db.session.commit()
        
        flash('Link updated successfully', 'success')
        return redirect(url_for('links.view_links'))
        
    tags_str = ", ".join(tag.name for tag in link.tags)
    return render_template('edit_link.html', link=link, collections=collections, tags_str=tags_str)

@links_bp.route('/links/<int:link_id>/delete', methods=['POST'])
@login_required
def delete_link(link_id):
    link = Link.query.filter_by(id=link_id, user_id=current_user.id).first_or_404()
    db.session.delete(link)
    db.session.commit()
    return jsonify({'success': True})

@links_bp.route('/links/<int:link_id>/toggle-favorite', methods=['POST'])
@login_required
def toggle_favorite(link_id):
    link = Link.query.filter_by(id=link_id, user_id=current_user.id).first_or_404()
    link.is_favorite = not link.is_favorite
    db.session.commit()
    return jsonify({'success': True, 'is_favorite': link.is_favorite})

@links_bp.route('/api/links/<int:link_id>', methods=['GET'])
@login_required
def get_link_details(link_id):
    link = Link.query.filter_by(id=link_id, user_id=current_user.id).first_or_404()
    
    tags_str = ", ".join(tag.name for tag in link.tags)
    
    return jsonify({
        'id': link.id,
        'title': link.title or '',
        'url': link.url or '',
        'description': link.description or '',
        'link_type': link.link_type or 'Website',
        'collection_id': link.collection_id or '',
        'tags': tags_str,
        'notes': link.notes or '',
        'is_favorite': link.is_favorite
    })
