def test_theme_cookie_ssr(auth_client):
    resp = auth_client.get('/', headers={'Cookie': 'theme=dark'})
    assert b'data-bs-theme="dark"' in resp.data
