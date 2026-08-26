from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import hash_password
from app.database import Base, get_db
from app.main import create_app
from app.models import FoodItem, Restaurant, User


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record) -> None:  # noqa: ANN001
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def user(db_session: Session) -> User:
    user = User(
        email="api-user@example.com",
        username="apiuser",
        display_name="API User",
        password_hash=hash_password("password123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def restaurant_payload(name: str = "Test Tiffin Room") -> dict[str, object]:
    return {
        "name": name,
        "description": "South Indian breakfast and coffee.",
        "address_line1": "12 Beach Road",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "postal_code": "600001",
        "country": "India",
        "latitude": "13.082700",
        "longitude": "80.270700",
    }


def create_restaurant(client: TestClient, name: str = "Test Tiffin Room") -> dict[str, object]:
    response = client.post("/restaurants", json=restaurant_payload(name))
    assert response.status_code == 201
    return response.json()


def create_food_item(client: TestClient, restaurant_id: int, user_id: int | None = None) -> dict[str, object]:
    payload: dict[str, object] = {
        "name": "Masala Dosa",
        "description": "Crisp dosa with spiced potato masala.",
        "price": "120.00",
        "currency": "INR",
    }
    if user_id is not None:
        payload["created_by_user_id"] = user_id

    response = client.post(f"/restaurants/{restaurant_id}/food-items", json=payload)
    assert response.status_code == 201
    return response.json()


def create_review(client: TestClient, food_item_id: int, user_id: int, rating: int = 5) -> dict[str, object]:
    response = client.post(
        f"/food-items/{food_item_id}/reviews",
        json={"user_id": user_id, "rating": rating, "body": "Excellent.", "would_order_again": True},
    )
    assert response.status_code == 201
    return response.json()


def test_create_restaurant(client: TestClient) -> None:
    restaurant = create_restaurant(client)

    assert restaurant["id"] > 0
    assert restaurant["name"] == "Test Tiffin Room"
    assert restaurant["city"] == "Chennai"


def test_retrieve_restaurant(client: TestClient) -> None:
    created = create_restaurant(client)

    response = client.get(f"/restaurants/{created['id']}")

    assert response.status_code == 200
    assert response.json()["name"] == created["name"]


def test_create_food_item(client: TestClient, user: User) -> None:
    restaurant = create_restaurant(client)

    food_item = create_food_item(client, restaurant["id"], user.id)

    assert food_item["restaurant_id"] == restaurant["id"]
    assert food_item["created_by_user_id"] == user.id
    assert food_item["normalized_name"] == "masala dosa"
    assert food_item["average_rating"] == "0.00"
    assert food_item["review_count"] == 0


def test_retrieve_food_items_for_restaurant(client: TestClient, user: User) -> None:
    restaurant = create_restaurant(client)
    food_item = create_food_item(client, restaurant["id"], user.id)

    response = client.get(f"/restaurants/{restaurant['id']}/food-items")

    assert response.status_code == 200
    assert response.json()[0]["id"] == food_item["id"]


def test_create_review_updates_aggregation(client: TestClient, user: User) -> None:
    restaurant = create_restaurant(client)
    food_item = create_food_item(client, restaurant["id"], user.id)

    review = create_review(client, food_item["id"], user.id, rating=4)

    assert review["rating"] == 4
    response = client.get(f"/food-items/{food_item['id']}")
    assert response.status_code == 200
    assert response.json()["average_rating"] == "4.00"
    assert response.json()["review_count"] == 1


def test_retrieve_reviews(client: TestClient, user: User) -> None:
    restaurant = create_restaurant(client)
    food_item = create_food_item(client, restaurant["id"], user.id)
    review = create_review(client, food_item["id"], user.id)

    response = client.get(f"/food-items/{food_item['id']}/reviews")

    assert response.status_code == 200
    assert response.json()[0]["id"] == review["id"]


def test_update_review_recomputes_average(client: TestClient, user: User) -> None:
    restaurant = create_restaurant(client)
    food_item = create_food_item(client, restaurant["id"], user.id)
    review = create_review(client, food_item["id"], user.id, rating=2)

    response = client.patch(f"/reviews/{review['id']}", json={"rating": 5, "body": "Much better."})

    assert response.status_code == 200
    assert response.json()["rating"] == 5
    food_item_response = client.get(f"/food-items/{food_item['id']}")
    assert food_item_response.json()["average_rating"] == "5.00"
    assert food_item_response.json()["review_count"] == 1


def test_delete_review_recomputes_average(client: TestClient, user: User, db_session: Session) -> None:
    second_user = User(
        email="second@example.com",
        username="second",
        display_name="Second User",
        password_hash=hash_password("password123"),
    )
    db_session.add(second_user)
    db_session.commit()
    db_session.refresh(second_user)

    restaurant = create_restaurant(client)
    food_item = create_food_item(client, restaurant["id"], user.id)
    review = create_review(client, food_item["id"], user.id, rating=5)
    create_review(client, food_item["id"], second_user.id, rating=3)

    response = client.delete(f"/reviews/{review['id']}")

    assert response.status_code == 204
    food_item_response = client.get(f"/food-items/{food_item['id']}")
    assert food_item_response.json()["average_rating"] == "3.00"
    assert food_item_response.json()["review_count"] == 1


def test_rating_validation(client: TestClient, user: User) -> None:
    restaurant = create_restaurant(client)
    food_item = create_food_item(client, restaurant["id"], user.id)

    response = client.post(f"/food-items/{food_item['id']}/reviews", json={"user_id": user.id, "rating": 6})

    assert response.status_code == 422


def test_404_cases(client: TestClient) -> None:
    assert client.get("/restaurants/999").status_code == 404
    assert client.get("/restaurants/999/food-items").status_code == 404
    assert client.post("/restaurants/999/food-items", json={"name": "Idli"}).status_code == 404
    assert client.get("/food-items/999").status_code == 404
    assert client.get("/food-items/999/reviews").status_code == 404
    assert client.post("/food-items/999/reviews", json={"user_id": 1, "rating": 5}).status_code == 404
    assert client.get("/reviews/999").status_code == 404
    assert client.patch("/reviews/999", json={"rating": 4}).status_code == 404
    assert client.delete("/reviews/999").status_code == 404


def test_pagination_for_restaurants(client: TestClient) -> None:
    create_restaurant(client, "First")
    second = create_restaurant(client, "Second")

    response = client.get("/restaurants?page=2&limit=1")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == second["id"]
