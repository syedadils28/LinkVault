from datetime import datetime
from app import db
from .tag import link_tag_table

class Link(db.Model):
    __tablename__ = 'links'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(2048), nullable=False)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    link_type = db.Column(db.String(50), default='Website')
    is_favorite = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'), nullable=True)
    
    # Relationships
    tags = db.relationship('Tag', secondary=link_tag_table, lazy='subquery',
        backref=db.backref('links', lazy=True))
        
    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'link_type': self.link_type,
            'is_favorite': self.is_favorite,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'collection': self.collection.name if self.collection else None,
            'tags': [tag.name for tag in self.tags]
        }
        
    def __repr__(self):
        return f'<Link {self.title or self.url}>'
