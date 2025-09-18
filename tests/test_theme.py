def test_theme_cookie_ssr(auth_client):
    auth_client.set_cookie('theme', 'dark')
    resp = auth_client.get('/')
    assert b'data-bs-theme="dark"' in resp.data


def test_theme_default_light(auth_client):
    resp = auth_client.get('/')
    assert b'data-bs-theme="light"' in resp.data
