from app.models.link import Link

def test_add_link_unauthenticated(client):
    response = client.post('/links/add', data={'url': 'https://example.com'})
    # Should redirect to login
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_add_link_authenticated(client, init_database, auth, app):
    auth.login()
    
    response = client.post('/links/add', data={
        'url': 'https://example.com',
        'title': 'Example Domain',
        'link_type': 'Website'
    })
    
    assert response.status_code == 302
    assert response.headers['Location'] == '/links'
    
    with app.app_context():
        link = Link.query.filter_by(url='https://example.com').first()
        assert link is not None
        assert link.title == 'Example Domain'
        assert link.link_type == 'Website'
