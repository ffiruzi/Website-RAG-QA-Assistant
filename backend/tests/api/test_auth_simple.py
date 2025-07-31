def test_auth_simple(client, test_db):
    """Test simplified auth flow."""
    # Create a test user
    from app.models.user import User
    from app.core.security import get_password_hash

    # Create a test user directly in the database
    test_user = User(
        email="simple@example.com",
        hashed_password=get_password_hash("simplepass"),
        full_name="Simple Test User",
        is_active=True,
        is_superuser=True
    )
    test_db.add(test_user)
    test_db.commit()

    # Try to login
    login_data = {
        "username": "simple@example.com",
        "password": "simplepass"
    }

    response = client.post("/api/v1/auth-simple/login", data=login_data)
    print(f"Simple login response: {response.status_code} - {response.text}")

    # Check response
    assert response.status_code == 200
    assert "access_token" in response.json()