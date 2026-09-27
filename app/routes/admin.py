from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.user import User
from app.models.link import Link
from app.models.collection import Collection

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access the admin panel.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    users = User.query.order_by(User.created_at.desc()).all()
    
    # Calculate stats for each user
    user_stats = []
    total_system_links = 0
    total_system_collections = 0
    
    for user in users:
        links_count = user.links.count()
        collections_count = user.collections.count()
        total_system_links += links_count
        total_system_collections += collections_count
        
        user_stats.append({
            'user': user,
            'links_count': links_count,
            'collections_count': collections_count
        })
        
    return render_template('admin/dashboard.html', 
                           user_stats=user_stats, 
                           total_users=len(users),
                           total_links=total_system_links,
                           total_collections=total_system_collections)

@admin_bp.route('/create_admin', methods=['GET', 'POST'])
@login_required
@admin_required
def create_admin():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('admin.create_admin'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('admin.create_admin'))
            
        admin_user = User(username=username, email=email, is_admin=True)
        admin_user.set_password(password)
        db.session.add(admin_user)
        db.session.commit()
        
        flash(f'Administrator account for {username} created successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/create_admin.html')

@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def user_delete(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Cannot delete an administrator account.', 'danger')
        return redirect(request.referrer or url_for('admin.dashboard'))
        
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} and all their content has been deleted.', 'success')
    return redirect(request.referrer or url_for('admin.dashboard'))

@admin_bp.route('/user/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
@admin_required
def user_toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot change your own administrator status.', 'warning')
        return redirect(request.referrer or url_for('admin.dashboard'))
        
    user.is_admin = not user.is_admin
    db.session.commit()
    status = "promoted to Admin" if user.is_admin else "demoted to User"
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(request.referrer or url_for('admin.dashboard'))

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    
    user_stats = []
    for user in users:
        links_count = user.links.count()
        collections_count = user.collections.count()
        
        user_stats.append({
            'user': user,
            'links_count': links_count,
            'collections_count': collections_count
        })
        
    return render_template('admin/manage_users.html', user_stats=user_stats)

@admin_bp.route('/user/<int:user_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot edit your own account from this panel. Please use your Profile page.', 'warning')
        return redirect(request.referrer or url_for('admin.manage_users'))
        
    new_username = request.form.get('username')
    new_email = request.form.get('email')
    
    if not new_username or not new_email:
        flash('Username and email are required.', 'danger')
        return redirect(request.referrer or url_for('admin.manage_users'))
        
    # Check if username or email is already taken by ANOTHER user
    existing_username = User.query.filter(User.username == new_username, User.id != user_id).first()
    existing_email = User.query.filter(User.email == new_email, User.id != user_id).first()
    
    if existing_username:
        flash('Username is already taken by another user.', 'danger')
        return redirect(request.referrer or url_for('admin.manage_users'))
        
    if existing_email:
        flash('Email is already taken by another user.', 'danger')
        return redirect(request.referrer or url_for('admin.manage_users'))
        
    user.username = new_username
    user.email = new_email
    db.session.commit()
    
    flash(f'User {user.username} has been updated successfully.', 'success')
    return redirect(request.referrer or url_for('admin.manage_users'))

@admin_bp.route('/links')
@login_required
@admin_required
def manage_links():
    links = Link.query.order_by(Link.created_at.desc()).all()
    return render_template('admin/manage_links.html', links=links)

@admin_bp.route('/links/<int:link_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_link(link_id):
    link = Link.query.get_or_404(link_id)
    
    link.title = request.form.get('title')
    link.url = request.form.get('url')
    link.description = request.form.get('description')
    link.link_type = request.form.get('link_type')
    
    db.session.commit()
    flash('Link updated successfully.', 'success')
    return redirect(url_for('admin.manage_links'))

@admin_bp.route('/links/<int:link_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    flash('Link deleted successfully.', 'success')
    return redirect(url_for('admin.manage_links'))

@admin_bp.route('/collections')
@login_required
@admin_required
def manage_collections():
    collections = Collection.query.order_by(Collection.created_at.desc()).all()
    return render_template('admin/manage_collections.html', collections=collections)

@admin_bp.route('/collections/<int:collection_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_collection(collection_id):
    collection = Collection.query.get_or_404(collection_id)
    
    name = request.form.get('name')
    if name:
        collection.name = name
    
    collection.description = request.form.get('description')
    
    db.session.commit()
    flash('Collection updated successfully.', 'success')
    return redirect(url_for('admin.manage_collections'))

@admin_bp.route('/collections/<int:collection_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_collection(collection_id):
    collection = Collection.query.get_or_404(collection_id)
    db.session.delete(collection)
    db.session.commit()
    flash('Collection deleted successfully.', 'success')
    return redirect(url_for('admin.manage_collections'))
