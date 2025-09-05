"""Placeholder tests for dashboard views."""

def test_dashboard_page(auth_client):
    response = auth_client.get("/dashboard")
    assert response.status_code == 200
