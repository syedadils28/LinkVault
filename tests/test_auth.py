def test_register(client):
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123'
    })
    # Should redirect to login page after successful registration
    assert response.status_code == 302
    assert response.headers['Location'] == '/login'

def test_login(client, init_database, auth):
    response = auth.login()
    # Should redirect to dashboard
    assert response.status_code == 302
    assert response.headers['Location'] == '/'

def test_logout(client, init_database, auth):
    auth.login()
    response = auth.logout()
    assert response.status_code == 302
    assert response.headers['Location'] == '/login'
