import pytest


def test_simulations_page_access(auth_client):
    resp = auth_client.get('/simulations/')
    assert resp.status_code == 200
    assert b'Simulations' in resp.data
