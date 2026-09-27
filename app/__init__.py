from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth
from config import Config
import os

# Extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
mail = Mail()
oauth = OAuth()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)
    
    # Register Google OAuth Client
    oauth.register(
        name='google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    # Register blueprints (routes)
    # We will import them here to avoid circular imports
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.links import links_bp
    from app.routes.collections import collections_bp
    from app.routes.imports import imports_bp
    from app.routes.exports import exports_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(links_bp)
    app.register_blueprint(collections_bp)
    app.register_blueprint(imports_bp)
    app.register_blueprint(exports_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_helpers():
        def get_icon_for_type(link_type):
            icon_map = {
                'Website': 'globe',
                'GitHub': 'code',
                'Documentation': 'book',
                'YouTube': 'play',
                'Article': 'file-text',
                'Research Paper': 'graduation-cap',
                'AI Tool': 'bot',
                'Development Tool': 'wrench',
                'Repository': 'folder-git',
                'Course': 'monitor-play',
                'Reference': 'bookmark',
                'Portfolio': 'briefcase',
                'Design': 'pen-tool',
                'Social Media': 'share-2',
                'Podcast': 'headphones',
                'Video': 'video',
                'E-commerce': 'shopping-cart',
                'Other': 'link'
            }
            return icon_map.get(link_type, 'link')
            
        return dict(get_icon_for_type=get_icon_for_type)

    return app

@login_manager.user_loader
def load_user(user_id):
    # This needs to be imported here to avoid circular import
    from app.models.user import User
    return User.query.get(int(user_id))
