from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    plain_password = db.Column(db.String(256), nullable=True)  # WARNING: SECURITY RISK
    auth_provider = db.Column(db.String(50), default='local', nullable=False)
    oauth_id = db.Column(db.String(256), nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    otp_secret = db.Column(db.String(10), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    collections = db.relationship('Collection', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    links = db.relationship('Link', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    tags = db.relationship('Tag', backref='owner', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.plain_password = password

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
