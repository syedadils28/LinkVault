import pytest
from app import create_app, db
from app.models.user import User

@pytest.fixture
def app():
    # Create a minimal config for testing
    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SECRET_KEY = 'test-secret'
        WTF_CSRF_ENABLED = False
        EXPORT_DIR = '/tmp/exports'

    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def auth(client):
    class AuthActions:
        def login(self, username='testuser', password='password'):
            return client.post('/login', data={'username': username, 'password': password})
            
        def logout(self):
            return client.get('/logout')
            
    return AuthActions()

@pytest.fixture
def init_database(app):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()
    return user
