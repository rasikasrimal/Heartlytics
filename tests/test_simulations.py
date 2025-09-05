"""Tests for simulations page."""

def test_simulations_page(auth_client):
    resp = auth_client.get("/simulations/?variable=age")
    assert resp.status_code == 200
    assert b'exercise-angina-chart' in resp.data
