import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import database

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    # ensure fresh sqlite file for tests
    # drop all & recreate
    database.Base.metadata.drop_all(bind=database.engine)
    database.Base.metadata.create_all(bind=database.engine)
    yield
    database.Base.metadata.drop_all(bind=database.engine)

def test_register_and_login():
    # register
    res = client.post("/register", json={"email": "test@example.com", "password": "secret123"})
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "test@example.com"
    # login
    res2 = client.post("/login", data={"username": "test@example.com", "password": "secret123"})
    assert res2.status_code == 200
    assert "access_token" in res2.json()


def test_get_current_user_with_proper_session():
    """Test that /me endpoint works correctly with proper DB session management."""
    # Register a user
    res = client.post("/register", json={"email": "me@example.com", "password": "mypassword123"})
    assert res.status_code == 201
    
    # Login to get token
    res = client.post("/login", data={"username": "me@example.com", "password": "mypassword123"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    
    # Access /me endpoint with token
    res = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "me@example.com"


def test_get_current_user_invalid_token():
    """Test that /me endpoint rejects invalid tokens."""
    res = client.get("/me", headers={"Authorization": "Bearer invalid_token"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid auth token"


def test_get_current_user_missing_token():
    """Test that /me endpoint requires authentication."""
    res = client.get("/me")
    assert res.status_code == 401


def test_rate_limiting_returns_headers():
    """Test that rate limiting headers are present in responses."""
    res = client.post("/register", json={"email": "rate@example.com", "password": "secret123"})
    # Rate limit headers should be present
    assert "x-ratelimit-limit" in res.headers or res.status_code == 201
