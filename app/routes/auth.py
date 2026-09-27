from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db, oauth, mail
from app.models.user import User
from werkzeug.security import check_password_hash
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
import secrets

auth_bp = Blueprint('auth', __name__)

def get_reset_token(user, expires_sec=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps({'user_id': user.id})

def verify_reset_token(token, expires_sec=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token, max_age=expires_sec)
    except:
        return None
    return User.query.get(data['user_id'])

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
            
        if user.is_admin:
            flash('Administrators must use the Admin Login portal.', 'warning')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=request.form.get('remember_me') == 'on')
        
        next_page = request.form.get('next') or request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('dashboard.index')
            
        return redirect(next_page)
        
    next_page = request.args.get('next')
    return render_template('auth.html', active_panel='login', next=next_page)

@auth_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.admin_login'))
            
        if not user.is_admin:
            flash('Access Denied. You are not an administrator.', 'error')
            return redirect(url_for('auth.admin_login'))
            
        login_user(user, remember=request.form.get('remember_me') == 'on')
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin_login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.register'))
            
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth.html', active_panel='register')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('dashboard.index'))

@auth_bp.route('/login/google')
def google_login():
    redirect_uri = url_for('auth.google_authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/login/google/authorize')
def google_authorize():
    try:
        token = oauth.google.authorize_access_token()
        userinfo = token.get('userinfo')
        if not userinfo:
            userinfo = oauth.google.userinfo()
    except Exception as e:
        flash('Google login failed.', 'error')
        return redirect(url_for('auth.login'))
        
    email = userinfo['email']
    google_id = userinfo['sub']
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        # Create a new user for Google login
        username = email.split('@')[0]
        # Ensure username uniqueness
        base_username = username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1
            
        user = User(
            username=username, 
            email=email,
            auth_provider='google',
            oauth_id=google_id
        )
        # Set a random impossible password for security
        user.set_password(secrets.token_urlsafe(32))
        db.session.add(user)
        db.session.commit()
    
    login_user(user)
    return redirect(url_for('dashboard.index'))

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = get_reset_token(user)
            reset_url = url_for('auth.reset_password_token', token=token, _external=True)
            
            # Print to console for development
            print("\n" + "="*50)
            print("PASSWORD RESET REQUEST")
            print(f"To: {user.email}")
            print(f"Link: {reset_url}")
            print("="*50 + "\n")
            
            try:
                msg = Message('Password Reset Request',
                            sender=current_app.config['MAIL_DEFAULT_SENDER'],
                            recipients=[user.email])
                msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request then simply ignore this email and no changes will be made.
'''
                mail.send(msg)
            except Exception as e:
                # If mail server fails, we still printed to console
                pass
                
        flash('An email has been sent with instructions to reset your password. (Check server console for demo link)', 'info')
        return redirect(url_for('auth.login'))
    return render_template('reset_request.html')

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    user = verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_password_request'))
    if request.method == 'POST':
        password = request.form.get('password')
        user.set_password(password)
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    return render_template('reset_token.html')
