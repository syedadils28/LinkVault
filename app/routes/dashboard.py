from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.link import Link
from app.models.collection import Collection
from app.models.tag import Tag
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import request, jsonify
from datetime import datetime
import os

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('landing.html')

    total_links = Link.query.filter_by(user_id=current_user.id).count()
    collections_count = Collection.query.filter_by(user_id=current_user.id).count()
    favorites_count = Link.query.filter_by(user_id=current_user.id, is_favorite=True).count()
    
    recent_links = Link.query.filter_by(user_id=current_user.id).order_by(Link.created_at.desc()).limit(5).all()
    favorite_links = Link.query.filter_by(user_id=current_user.id, is_favorite=True).order_by(Link.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                           total_links=total_links, 
                           collections_count=collections_count,
                           favorites_count=favorites_count,
                           recent_links=recent_links,
                           favorite_links=favorite_links)

@dashboard_bp.route('/api/contact', methods=['POST'])
def contact_form():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')

        if not all([name, email, subject, message]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400

        # Setup Google Sheets API
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        
        # Path to the credentials file (project root)
        creds_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'credentials.json')
        
        if not os.path.exists(creds_path):
            return jsonify({'success': False, 'message': 'credentials.json not found. Please create Service Account and download credentials.json.'}), 500

        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)

        # Open the sheet
        sheet = client.open('LinkVault Contacts').sheet1

        # Append row
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([timestamp, name, email, subject, message])

        return jsonify({'success': True, 'message': 'Message sent successfully!'})
    except gspread.exceptions.SpreadsheetNotFound:
        return jsonify({'success': False, 'message': 'Spreadsheet "LinkVault Contacts" not found or not shared with the service account.'}), 500
    except Exception as e:
        print(f"Contact form error: {str(e)}")
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500

@dashboard_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    from flask import request, flash, current_app
    from werkzeug.utils import secure_filename
    from app import db
    import os
    import uuid
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        otp = request.form.get('otp')
        
        # Simple validation
        if not username or not email:
            flash('Username and email are required.', 'error')
        # Note: email is no longer updated here; it's done via AJAX modal.
        current_user.username = username
        
        # Handle profile image upload
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename:
                # Basic validation
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
                ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
                
                if ext in allowed_extensions:
                    # Generate safe, unique filename
                    filename = secure_filename(f"{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}")
                    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
                    
                    # Ensure directory exists
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    # Save file
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                    
                    # Delete old image if it exists and isn't a default
                    if current_user.profile_image:
                        old_path = os.path.join(upload_folder, current_user.profile_image)
                        if os.path.exists(old_path):
                            try:
                                os.remove(old_path)
                            except OSError:
                                pass
                                
                    current_user.profile_image = filename
                else:
                    flash('Invalid image format. Allowed: PNG, JPG, JPEG, GIF, WEBP.', 'error')
            
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard.profile'))
        
    return render_template('profile.html')

@dashboard_bp.route('/profile/image', methods=['POST'])
@login_required
def upload_image():
    from flask import request, jsonify, current_app
    from werkzeug.utils import secure_filename
    from app import db
    import os
    import uuid
    
    if 'profile_image' not in request.files:
        return jsonify({'success': False, 'error': 'No image provided'})
        
    file = request.files['profile_image']
    if file and file.filename:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        
        if ext in allowed_extensions:
            filename = secure_filename(f"{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}")
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            if current_user.profile_image:
                old_path = os.path.join(upload_folder, current_user.profile_image)
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except OSError:
                        pass
                        
            current_user.profile_image = filename
            db.session.commit()
            return jsonify({'success': True, 'image_url': url_for('static', filename='uploads/profiles/' + filename)})
        
    return jsonify({'success': False, 'error': 'Invalid file format'})

@dashboard_bp.route('/profile/image', methods=['DELETE'])
@login_required
def remove_image():
    from flask import jsonify, current_app
    from app import db
    import os
    
    if current_user.profile_image:
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
        old_path = os.path.join(upload_folder, current_user.profile_image)
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass
                
        current_user.profile_image = None
        db.session.commit()
        return jsonify({'success': True})
        
    return jsonify({'success': False, 'error': 'No image to remove'})

@dashboard_bp.route('/profile/send-otp', methods=['POST'])
@login_required
def send_otp():
    from flask import jsonify, current_app, request
    from app import db, mail
    from flask_mail import Message
    import random
    from datetime import datetime, timedelta
    
    # Check if a target_email is provided, else fallback to current user's email
    target_email = current_user.email
    if request.is_json:
        data = request.get_json()
        if data and 'target_email' in data:
            target_email = data['target_email']
    
    # Generate 6 digit OTP
    otp = str(random.randint(100000, 999999))
    
    current_user.otp_secret = otp
    current_user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
    db.session.commit()
    
    try:
        msg = Message('Your Password Reset OTP - LinkVault',
                      sender=current_app.config['MAIL_DEFAULT_SENDER'],
                      recipients=[target_email])
        msg.body = f'''Hello {current_user.username},

You have requested to make a security change. Please use the following 6-digit OTP to confirm this action:

{otp}

This OTP will expire in 10 minutes. If you did not request this change, please secure your account immediately.

Best regards,
LinkVault Team
'''
        mail.send(msg)
        # Also print to console for easy local development without an email server
        print(f"\n[DEMO] OTP for {target_email} is: {otp}\n")
        return jsonify({'success': True, 'message': 'OTP sent successfully'})
    except Exception as e:
        # If email fails, print to console for dev
        print(f"\n[DEMO - Mail failed] OTP for {target_email} is: {otp}\n")
        return jsonify({'success': True, 'message': 'OTP generated (Check console)'})

@dashboard_bp.route('/profile/update-email', methods=['POST'])
@login_required
def update_email():
    from flask import request, jsonify
    from app import db
    
    data = request.get_json()
    new_email = data.get('new_email')
    
    if not new_email:
        return jsonify({'success': False, 'error': 'New email is required.'})
        
    current_user.email = new_email
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Email updated successfully!'})

@dashboard_bp.route('/profile/update-password', methods=['POST'])
@login_required
def update_password():
    from flask import request, jsonify
    from app import db
    
    data = request.get_json()
    current_pwd = data.get('current_password')
    new_pwd = data.get('new_password')
    
    if not current_pwd or not new_pwd:
        return jsonify({'success': False, 'error': 'Current and new password are required.'})
        
    if not current_user.check_password(current_pwd):
        return jsonify({'success': False, 'error': 'Incorrect current password.'})
        
    current_user.set_password(new_pwd)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Password updated successfully!'})


@dashboard_bp.route('/tools')
@login_required
def tools():
    return render_template('tools.html')
