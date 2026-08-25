import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]

def test_auth_registration_and_login():
    email = "unittest_user@eco.fashion"
    reg_payload = {
        "email": email,
        "password": "testpassword123",
        "full_name": "Test Designer"
    }
    res = client.post("/api/v1/auth/register", json=reg_payload)
    assert res.status_code in [201, 400]

    login_payload = {
        "email": email,
        "password": "testpassword123"
    }
    res_login = client.post("/api/v1/auth/login", json=login_payload)
    assert res_login.status_code == 200
    token_data = res_login.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email
