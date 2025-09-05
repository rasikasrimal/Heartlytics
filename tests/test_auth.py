import re


def test_login_fields_blank(client):
    res = client.get('/auth/login')
    html = res.data.decode()
    identifier_input = re.search(r'<input[^>]*name="identifier"[^>]*>', html).group(0)
    password_input = re.search(r'<input[^>]*name="password"[^>]*>', html).group(0)
    assert 'value=' not in identifier_input
    assert 'value=' not in password_input
    assert 'autocomplete="off"' in identifier_input
    assert 'autocomplete="off"' in password_input
