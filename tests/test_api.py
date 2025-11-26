import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.db.database import get_db
from src.db.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_game(test_db):
    response = client.post("/api/v1/games", json={"player_name": "TestPlayer"})
    assert response.status_code == 200
    data = response.json()
    assert data["players"]["X"] == "TestPlayer"
    assert data["current_player"] == "X"
    assert data["is_active"] == True


def test_get_game(test_db):
    create_response = client.post("/api/v1/games", json={"player_name": "TestPlayer"})
    game_id = create_response.json()["id"]

    response = client.get(f"/api/v1/games/{game_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == game_id
    assert data["players"]["X"] == "TestPlayer"


def test_make_move(test_db):
    create_response = client.post("/api/v1/games", json={"player_name": "Player1"})
    game_id = create_response.json()["id"]

    move_response = client.post(
        f"/api/v1/games/{game_id}/move",
        json={"player": "X", "row": 0, "col": 0}
    )
    assert move_response.status_code == 200
    data = move_response.json()
    assert data["board"][0][0] == "X"
    assert data["current_player"] == "O"