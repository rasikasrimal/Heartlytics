"""Tests for simulations page."""

def test_simulations_page(auth_client):
    resp = auth_client.get("/simulations/")
    assert resp.status_code == 200
    assert b"Prediction Result" not in resp.data

    resp = auth_client.post("/simulations/run", data={"variable": "age"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "exercise_angina" in data["results"]
    assert data["results"]["exercise_angina"]["variable"] == "age"
