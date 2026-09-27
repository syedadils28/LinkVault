from datetime import datetime
from app import db

class Collection(db.Model):
    __tablename__ = 'collections'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50), default='folder')
    is_public = db.Column(db.Boolean, default=False)
    share_token = db.Column(db.String(100), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    links = db.relationship('Link', backref='collection', lazy='dynamic')
    
    def __repr__(self):
        return f'<Collection {self.name}>'
