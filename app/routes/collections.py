from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.collection import Collection
import uuid

collections_bp = Blueprint('collections', __name__)

@collections_bp.route('/collections')
@login_required
def view_collections():
    collections = Collection.query.filter_by(user_id=current_user.id).order_by(Collection.created_at.desc()).all()
    return render_template('collections.html', collections=collections)

@collections_bp.route('/collections/add', methods=['POST'])
@login_required
def add_collection():
    name = request.form.get('name')
    description = request.form.get('description')
    icon = request.form.get('icon', 'folder')
    
    if not name:
        flash('Collection name is required', 'error')
        return redirect(url_for('collections.view_collections'))
        
    collection = Collection(name=name, description=description, icon=icon, user_id=current_user.id)
    db.session.add(collection)
    db.session.commit()
    
    flash('Collection created', 'success')
    return redirect(url_for('collections.view_collections'))

@collections_bp.route('/collections/<int:collection_id>')
@login_required
def collection_detail(collection_id):
    collection = Collection.query.filter_by(id=collection_id, user_id=current_user.id).first_or_404()
    return render_template('collection_detail.html', collection=collection)

@collections_bp.route('/collections/<int:collection_id>/delete', methods=['POST'])
@login_required
def delete_collection(collection_id):
    collection = Collection.query.filter_by(id=collection_id, user_id=current_user.id).first_or_404()
    
    # We cascade delete in the model but let's just make sure
    db.session.delete(collection)
    db.session.commit()
    
    return jsonify({'success': True})

@collections_bp.route('/collections/<int:collection_id>/edit', methods=['POST'])
@login_required
def edit_collection(collection_id):
    collection = Collection.query.filter_by(id=collection_id, user_id=current_user.id).first_or_404()
    
    name = request.form.get('name')
    if name:
        collection.name = name
    
    collection.description = request.form.get('description')
    
    icon = request.form.get('icon')
    if icon:
        collection.icon = icon
        
    db.session.commit()
    flash('Collection updated successfully', 'success')
    return redirect(request.referrer or url_for('collections.view_collections'))

@collections_bp.route('/collections/<int:collection_id>/toggle-share', methods=['POST'])
@login_required
def toggle_share(collection_id):
    collection = Collection.query.filter_by(id=collection_id, user_id=current_user.id).first_or_404()
    
    # Toggle public state
    collection.is_public = not collection.is_public
    
    # Generate token if making public and none exists
    if collection.is_public and not collection.share_token:
        collection.share_token = str(uuid.uuid4())
        
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'is_public': collection.is_public,
        'share_url': url_for('collections.shared_collection', share_token=collection.share_token, _external=True) if collection.is_public else None
    })

@collections_bp.route('/shared/<share_token>')
def shared_collection(share_token):
    collection = Collection.query.filter_by(share_token=share_token, is_public=True).first_or_404()
    
    # Get all links for this collection
    # Note: we need to import Link. We'll do it locally to avoid circular imports just in case
    from app.models.link import Link
    links = Link.query.filter_by(collection_id=collection.id).order_by(Link.created_at.desc()).all()
    
    return render_template('shared_collection.html', collection=collection, links=links)
