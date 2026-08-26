from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas import FoodItemCreate, RestaurantCreate, ReviewCreate, UserCreate, normalize_food_item_name


def test_normalize_food_item_name() -> None:
    assert normalize_food_item_name("  Ghee   Podi IDLI ") == "ghee podi idli"


def test_user_create_validates_username_length() -> None:
    with pytest.raises(ValidationError):
        UserCreate(email="test@example.com", username="ab", display_name="Test User", password="password123")


def test_restaurant_create_validates_latitude() -> None:
    with pytest.raises(ValidationError):
        RestaurantCreate(
            name="Test",
            address_line1="123 Main Street",
            city="Chennai",
            state="Tamil Nadu",
            latitude=Decimal("91"),
        )


def test_food_item_create_normalizes_currency() -> None:
    item = FoodItemCreate(name="Dosa", price=Decimal("100.00"), currency="inr")

    assert item.currency == "INR"


def test_review_create_validates_rating_range() -> None:
    with pytest.raises(ValidationError):
        ReviewCreate(user_id=1, rating=6)
