import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.config import get_db
from networks.app.models import Base  # import your SQLAlchemy Base

# --- Use a SQLite in-memory database for tests ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # or use ":memory:" for purely in-memory

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the DB dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply the override
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# --- Setup / Teardown ---
@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# --- TESTS ---

def test_assign_user_fails_when_user_not_found():
    response = client.post("/network/assign-user", json={
        "user_id": "non-existent-id",
        "parranage_code": "ABC123"
    })
    assert response.status_code == 500 or response.status_code == 400
    assert "not found" in response.json()["detail"].lower()

def test_create_commercial_network_invalid_id():
    response = client.post("/network/create-commercial-network", json={
        "commercial_id": "invalid-id"
    })
    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower()

def test_calculate_position_invalid_plan():
    response = client.post("/network/calculate-position", json={
        "network_id": "some-id",
        "plan_type": "invalid_plan_format"
    })
    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()

def test_get_network_tree_empty():
    response = client.get("/network/users/some-user-id/network-tree")
    assert response.status_code == 200
    assert response.json() == {}
