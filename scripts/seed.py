from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import hash_password
from app.database import SessionLocal
from app.models import FoodItem, Restaurant, Review, User
from app.schemas import normalize_food_item_name


def recompute_food_item_stats(db: Session, food_item: FoodItem) -> None:
    ratings = [review.rating for review in food_item.reviews]
    food_item.review_count = len(ratings)
    food_item.average_rating = (
        Decimal("0.00") if not ratings else (Decimal(sum(ratings)) / Decimal(len(ratings))).quantize(Decimal("0.01"))
    )


def seed() -> None:
    db = SessionLocal()
    try:
        existing = db.scalar(select(User).where(User.email == "ananya@example.com"))
        if existing is not None:
            print("Seed data already exists; nothing to do.")
            return

        users = [
            User(
                email="ananya@example.com",
                username="ananya",
                display_name="Ananya",
                password_hash=hash_password("password123"),
            ),
            User(
                email="karthik@example.com",
                username="karthik",
                display_name="Karthik",
                password_hash=hash_password("password123"),
            ),
            User(
                email="meera@example.com",
                username="meera",
                display_name="Meera",
                password_hash=hash_password("password123"),
            ),
        ]
        db.add_all(users)

        restaurants = [
            Restaurant(
                name="Murugan Idli Shop",
                description="Chennai staple for soft idlis, podi, and filter coffee.",
                address_line1="6th Avenue, Besant Nagar",
                city="Chennai",
                state="Tamil Nadu",
                postal_code="600090",
                latitude=Decimal("13.000600"),
                longitude=Decimal("80.266800"),
            ),
            Restaurant(
                name="Buhari Hotel",
                description="Classic Chennai restaurant known for biryani and South Indian comfort food.",
                address_line1="Anna Salai",
                city="Chennai",
                state="Tamil Nadu",
                postal_code="600002",
                latitude=Decimal("13.064900"),
                longitude=Decimal("80.269700"),
            ),
            Restaurant(
                name="Amadora Gourmet Ice Cream",
                description="Small-batch ice cream and desserts.",
                address_line1="Wallace Garden 3rd Street, Nungambakkam",
                city="Chennai",
                state="Tamil Nadu",
                postal_code="600006",
                latitude=Decimal("13.060500"),
                longitude=Decimal("80.249600"),
            ),
        ]
        db.add_all(restaurants)
        db.flush()

        food_items = [
            FoodItem(
                restaurant=restaurants[0],
                created_by=users[0],
                name="Ghee Podi Idli",
                normalized_name=normalize_food_item_name("Ghee Podi Idli"),
                description="Mini idlis tossed with ghee and podi.",
                price=Decimal("145.00"),
            ),
            FoodItem(
                restaurant=restaurants[0],
                created_by=users[1],
                name="Filter Coffee",
                normalized_name=normalize_food_item_name("Filter Coffee"),
                description="Strong South Indian filter coffee.",
                price=Decimal("55.00"),
            ),
            FoodItem(
                restaurant=restaurants[1],
                created_by=users[1],
                name="Chicken Biryani",
                normalized_name=normalize_food_item_name("Chicken Biryani"),
                description="Fragrant Chennai-style chicken biryani.",
                price=Decimal("280.00"),
            ),
            FoodItem(
                restaurant=restaurants[2],
                created_by=users[2],
                name="Salted Butter Caramel Ice Cream",
                normalized_name=normalize_food_item_name("Salted Butter Caramel Ice Cream"),
                description="Rich caramel ice cream with a salty finish.",
                price=Decimal("220.00"),
            ),
        ]
        db.add_all(food_items)
        db.flush()

        reviews = [
            Review(user=users[0], food_item=food_items[2], rating=5, body="Deep flavor and generous portion.", would_order_again=True),
            Review(user=users[1], food_item=food_items[0], rating=5, body="Exactly the kind of podi hit I want.", would_order_again=True),
            Review(user=users[2], food_item=food_items[0], rating=4, body="Soft idlis, lovely ghee aroma.", would_order_again=True),
            Review(user=users[0], food_item=food_items[3], rating=4, body="Creamy and balanced, not too sweet.", would_order_again=True),
        ]
        db.add_all(reviews)
        db.flush()

        for food_item in food_items:
            recompute_food_item_stats(db, food_item)

        db.commit()
        print("Seed data created.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
