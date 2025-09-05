"""Placeholder tests for prediction features."""

def test_index_route(auth_client):
    response = auth_client.get("/")
    assert response.status_code == 200
