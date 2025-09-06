def test_theme_cookie_ssr(auth_client):
    resp = auth_client.get('/', headers={'Cookie': 'theme=dark'})
    assert b'data-bs-theme="dark"' in resp.data


def test_theme_default_light(auth_client):
    resp = auth_client.get('/')
    assert b'data-bs-theme="light"' in resp.data
