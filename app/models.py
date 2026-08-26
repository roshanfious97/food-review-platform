from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    reviews: Mapped[list["Review"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    created_food_items: Mapped[list["FoodItem"]] = relationship(back_populates="created_by")

    __table_args__ = (
        CheckConstraint("length(username) >= 3", name="ck_users_username_min_length"),
        CheckConstraint("length(display_name) >= 1", name="ck_users_display_name_min_length"),
    )


class Restaurant(TimestampMixin, Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    address_line1: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line2: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    state: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    postal_code: Mapped[str | None] = mapped_column(String(20), index=True)
    country: Mapped[str] = mapped_column(String(100), default="India", nullable=False)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    phone: Mapped[str | None] = mapped_column(String(40))
    website_url: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    food_items: Mapped[list["FoodItem"]] = relationship(back_populates="restaurant", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("length(name) >= 1", name="ck_restaurants_name_min_length"),
        CheckConstraint("latitude IS NULL OR (latitude >= -90 AND latitude <= 90)", name="ck_restaurants_latitude_range"),
        CheckConstraint(
            "longitude IS NULL OR (longitude >= -180 AND longitude <= 180)", name="ck_restaurants_longitude_range"
        ),
        Index("ix_restaurants_location", "city", "state"),
    )


class FoodItem(TimestampMixin, Base):
    __tablename__ = "food_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id", ondelete="CASCADE"), index=True, nullable=False)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    is_available: Mapped[bool] = mapped_column(default=True, nullable=False)
    average_rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=Decimal("0.00"), nullable=False)
    review_count: Mapped[int] = mapped_column(default=0, nullable=False)

    restaurant: Mapped["Restaurant"] = relationship(back_populates="food_items")
    created_by: Mapped["User | None"] = relationship(back_populates="created_food_items")
    reviews: Mapped[list["Review"]] = relationship(back_populates="food_item", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("restaurant_id", "normalized_name", name="uq_food_items_restaurant_normalized_name"),
        CheckConstraint("length(name) >= 1", name="ck_food_items_name_min_length"),
        CheckConstraint("price IS NULL OR price >= 0", name="ck_food_items_price_non_negative"),
        CheckConstraint("average_rating >= 0 AND average_rating <= 5", name="ck_food_items_average_rating_range"),
        CheckConstraint("review_count >= 0", name="ck_food_items_review_count_non_negative"),
        Index("ix_food_items_restaurant_name", "restaurant_id", "name"),
    )


class Review(TimestampMixin, Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    food_item_id: Mapped[int] = mapped_column(ForeignKey("food_items.id", ondelete="CASCADE"), index=True, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    body: Mapped[str | None] = mapped_column(Text)
    would_order_again: Mapped[bool | None] = mapped_column()

    user: Mapped["User"] = relationship(back_populates="reviews")
    food_item: Mapped["FoodItem"] = relationship(back_populates="reviews")

    __table_args__ = (
        UniqueConstraint("user_id", "food_item_id", name="uq_reviews_user_food_item"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_reviews_rating_range"),
        CheckConstraint("body IS NULL OR length(body) <= 5000", name="ck_reviews_body_max_length"),
        Index("ix_reviews_food_item_created_at", "food_item_id", "created_at"),
    )
