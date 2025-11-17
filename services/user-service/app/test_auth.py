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
