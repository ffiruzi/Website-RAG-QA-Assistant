def test_endpoints_exist(client):
    """Test that all endpoints exist."""
    endpoints = [
        # Auth endpoints
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/test-token",

        # User endpoints
        "/api/v1/users/",

        # Website endpoints
        "/api/v1/websites/",

        # Simple auth endpoint for comparison
        "/api/v1/auth-simple/login"
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        # We expect either 405 (Method Not Allowed) or 401 (Unauthorized)
        # We should NOT get a 404 (Not Found)
        assert response.status_code != 404, f"Endpoint {endpoint} not found (404)"
        print(f"Endpoint {endpoint}: {response.status_code}")