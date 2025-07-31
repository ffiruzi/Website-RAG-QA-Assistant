def test_auth_endpoints_exist(client):
    """Test that the auth endpoints exist."""
    # Check login endpoint (should exist)
    response = client.get("/api/v1/auth/login")
    assert response.status_code != 404, "Auth login endpoint not found"

    # Check register endpoint (should exist)
    response = client.get("/api/v1/auth/register")
    assert response.status_code != 404, "Auth register endpoint not found"

    # Check test-token endpoint (should exist)
    response = client.get("/api/v1/auth/test-token")
    assert response.status_code != 404, "Auth test-token endpoint not found"


def test_auth_flow(client, test_db):
    """Test the full auth flow with registration and login."""
    # Register a new user
    user_data = {
        "email": "testflow@example.com",
        "password": "securepassword",
        "full_name": "Test Flow User"
    }

    register_response = client.post("/api/v1/auth/register", json=user_data)
    assert register_response.status_code == 201, f"Registration failed: {register_response.text}"

    # Login with new user
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }

    login_response = client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    assert "access_token" in login_response.json()

    # Get token and test it
    token = login_response.json()["access_token"]

    # Test token with test-token endpoint
    test_token_response = client.post(
        "/api/v1/auth/test-token",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert test_token_response.status_code == 200, f"Token test failed: {test_token_response.text}"
    assert test_token_response.json()["email"] == user_data["email"]