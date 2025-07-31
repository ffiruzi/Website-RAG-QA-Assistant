def test_direct_login(client):
    """Test the direct login endpoint."""
    login_data = {
        "username": "test@example.com",
        "password": "password"
    }

    response = client.post("/direct-login", data=login_data)
    print(f"Direct login response: {response.status_code} - {response.text}")

    assert response.status_code == 200
    assert response.json()["username"] == "test@example.com"