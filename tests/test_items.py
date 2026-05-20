import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

# ── In-memory SQLite DB for tests (no PostgreSQL needed locally) ──
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    """Create tables before tests, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Helper ────────────────────────────────────────────────────────
ITEM_PAYLOAD = {
    "name": "Test Laptop",
    "description": "A test item",
    "price": 150000,
    "is_available": True,
}


# ── Tests (code)─────────────────────────────────────────────────────────


class TestHealthCheck:
    def test_root_returns_ok(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestCreateItem:
    def test_create_item_success(self, client):
        response = client.post("/api/v1/items/", json=ITEM_PAYLOAD)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == ITEM_PAYLOAD["name"]
        assert data["price"] == ITEM_PAYLOAD["price"]
        assert "id" in data

    def test_create_item_missing_name(self, client):
        response = client.post("/api/v1/items/", json={"price": 100})
        assert response.status_code == 422

    def test_create_item_negative_price(self, client):
        response = client.post("/api/v1/items/", json={**ITEM_PAYLOAD, "price": -1})
        assert response.status_code == 422


class TestReadItems:
    def test_list_items(self, client):
        response = client.get("/api/v1/items/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_item_by_id(self, client):
        # Create first
        create_resp = client.post("/api/v1/items/", json=ITEM_PAYLOAD)
        item_id = create_resp.json()["id"]
        # Then read
        response = client.get(f"/api/v1/items/{item_id}")
        assert response.status_code == 200
        assert response.json()["id"] == item_id

    def test_get_nonexistent_item(self, client):
        response = client.get("/api/v1/items/99999")
        assert response.status_code == 404


class TestUpdateItem:
    def test_update_item_price(self, client):
        create_resp = client.post("/api/v1/items/", json=ITEM_PAYLOAD)
        item_id = create_resp.json()["id"]
        response = client.put(f"/api/v1/items/{item_id}", json={"price": 99999})
        assert response.status_code == 200
        assert response.json()["price"] == 99999

    def test_update_nonexistent_item(self, client):
        response = client.put("/api/v1/items/99999", json={"price": 100})
        assert response.status_code == 404


class TestDeleteItem:
    def test_delete_item(self, client):
        create_resp = client.post("/api/v1/items/", json=ITEM_PAYLOAD)
        item_id = create_resp.json()["id"]
        response = client.delete(f"/api/v1/items/{item_id}")
        assert response.status_code == 200
        # Confirm it's gone
        get_resp = client.get(f"/api/v1/items/{item_id}")
        assert get_resp.status_code == 404

    def test_delete_nonexistent_item(self, client):
        response = client.delete("/api/v1/items/99999")
        assert response.status_code == 404
