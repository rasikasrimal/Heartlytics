"""Placeholder tests for upload workflow."""

def test_upload_page(auth_client):
    response = auth_client.get("/upload")
    assert response.status_code == 200
