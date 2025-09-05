"""Tests for simulations page."""

def test_simulations_page(auth_client):
    resp = auth_client.get("/simulations/")
    assert resp.status_code == 200
    assert b"exercise-angina-chart" not in resp.data

    resp = auth_client.post("/simulations/", data={"variable": "age"})
    assert resp.status_code == 200
    assert b"exercise-angina-chart" in resp.data
    assert b"Heart disease risk change with Age" in resp.data
    assert b"You\\'re here" in resp.data
    assert b"What-If" not in resp.data
    assert b"Age Projection" not in resp.data
