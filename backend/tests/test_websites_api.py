import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.models.website import Website

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db dependency
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def db():
    # Create clean database for each test
    Base.metadata.create_all(bind=engine)
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_create_website(db):
    response = client.post(
        "/api/websites/",
        json={
            "url": "https://example.com",
            "name": "Example Website",
            "description": "This is an example website",
            "is_active": True,
            "sitemap_url": "https://example.com/sitemap.xml"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["url"] == "https://example.com"
    assert data["name"] == "Example Website"
    assert data["description"] == "This is an example website"
    assert data["is_active"] is True
    assert data["sitemap_url"] == "https://example.com/sitemap.xml"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_website_invalid_url(db):
    response = client.post(
        "/api/websites/",
        json={
            "url": "invalid-url",
            "name": "Example Website",
        },
    )
    assert response.status_code == 422  # Validation error


def test_read_websites(db):
    # Create test websites
    website1 = Website(url="https://example1.com", name="Example 1")
    website2 = Website(url="https://example2.com", name="Example 2")
    db.add(website1)
    db.add(website2)
    db.commit()

    response = client.get("/api/websites/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["url"] == "https://example1.com"
    assert data[1]["url"] == "https://example2.com"


def test_read_website(db):
    # Create test website
    website = Website(url="https://example.com", name="Example")
    db.add(website)
    db.commit()

    response = client.get(f"/api/websites/{website.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == "https://example.com"
    assert data["name"] == "Example"
    assert "id" in data


def test_read_website_not_found(db):
    response = client.get("/api/websites/999")
    assert response.status_code == 404


def test_update_website(db):
    # Create test website
    website = Website(url="https://example.com", name="Example")
    db.add(website)
    db.commit()

    response = client.put(
        f"/api/websites/{website.id}",
        json={
            "name": "Updated Name",
            "description": "Updated description"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "Updated description"
    # URL should remain unchanged
    assert data["url"] == "https://example.com"


def test_update_website_not_found(db):
    response = client.put(
        "/api/websites/999",
        json={"name": "Updated Name"},
    )
    assert response.status_code == 404


def test_update_website_duplicate_url(db):
    # Create test websites
    website1 = Website(url="https://example1.com", name="Example 1")
    website2 = Website(url="https://example2.com", name="Example 2")
    db.add(website1)
    db.add(website2)
    db.commit()

    # Try to update website1 with website2's URL
    response = client.put(
        f"/api/websites/{website1.id}",
        json={"url": "https://example2.com"},
    )
    assert response.status_code == 400  # Bad request, URL already exists


def test_delete_website(db):
    # Create test website
    website = Website(url="https://example.com", name="Example")
    db.add(website)
    db.commit()

    response = client.delete(f"/api/websites/{website.id}")
    assert response.status_code == 204  # No content

    # Verify website was deleted
    db_website = db.query(Website).filter(Website.id == website.id).first()
    assert db_website is None


def test_delete_website_not_found(db):
    response = client.delete("/api/websites/999")
    assert response.status_code == 404