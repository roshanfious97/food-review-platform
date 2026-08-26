"""initial models

Revision ID: 0001_initial_models
Revises:
Create Date: 2026-08-26 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_models"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "restaurants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("address_line1", sa.String(length=255), nullable=False),
        sa.Column("address_line2", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=False),
        sa.Column("postal_code", sa.String(length=20), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=False),
        sa.Column("latitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("website_url", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("latitude IS NULL OR (latitude >= -90 AND latitude <= 90)", name="ck_restaurants_latitude_range"),
        sa.CheckConstraint("length(name) >= 1", name="ck_restaurants_name_min_length"),
        sa.CheckConstraint("longitude IS NULL OR (longitude >= -180 AND longitude <= 180)", name="ck_restaurants_longitude_range"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_restaurants_city", "restaurants", ["city"], unique=False)
    op.create_index("ix_restaurants_location", "restaurants", ["city", "state"], unique=False)
    op.create_index("ix_restaurants_name", "restaurants", ["name"], unique=False)
    op.create_index("ix_restaurants_postal_code", "restaurants", ["postal_code"], unique=False)
    op.create_index("ix_restaurants_state", "restaurants", ["state"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("length(display_name) >= 1", name="ck_users_display_name_min_length"),
        sa.CheckConstraint("length(username) >= 3", name="ck_users_username_min_length"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "food_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("restaurant_id", sa.Integer(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("normalized_name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        sa.Column("average_rating", sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column("review_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("average_rating >= 0 AND average_rating <= 5", name="ck_food_items_average_rating_range"),
        sa.CheckConstraint("length(name) >= 1", name="ck_food_items_name_min_length"),
        sa.CheckConstraint("price IS NULL OR price >= 0", name="ck_food_items_price_non_negative"),
        sa.CheckConstraint("review_count >= 0", name="ck_food_items_review_count_non_negative"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("restaurant_id", "normalized_name", name="uq_food_items_restaurant_normalized_name"),
    )
    op.create_index("ix_food_items_created_by_user_id", "food_items", ["created_by_user_id"], unique=False)
    op.create_index("ix_food_items_name", "food_items", ["name"], unique=False)
    op.create_index("ix_food_items_restaurant_id", "food_items", ["restaurant_id"], unique=False)
    op.create_index("ix_food_items_restaurant_name", "food_items", ["restaurant_id", "name"], unique=False)

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("food_item_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Numeric(precision=2, scale=1), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("would_order_again", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("body IS NULL OR length(body) <= 5000", name="ck_reviews_body_max_length"),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_reviews_rating_range"),
        sa.ForeignKeyConstraint(["food_item_id"], ["food_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "food_item_id", name="uq_reviews_user_food_item"),
    )
    op.create_index("ix_reviews_food_item_created_at", "reviews", ["food_item_id", "created_at"], unique=False)
    op.create_index("ix_reviews_food_item_id", "reviews", ["food_item_id"], unique=False)
    op.create_index("ix_reviews_user_id", "reviews", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_reviews_user_id", table_name="reviews")
    op.drop_index("ix_reviews_food_item_id", table_name="reviews")
    op.drop_index("ix_reviews_food_item_created_at", table_name="reviews")
    op.drop_table("reviews")
    op.drop_index("ix_food_items_restaurant_name", table_name="food_items")
    op.drop_index("ix_food_items_restaurant_id", table_name="food_items")
    op.drop_index("ix_food_items_name", table_name="food_items")
    op.drop_index("ix_food_items_created_by_user_id", table_name="food_items")
    op.drop_table("food_items")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_restaurants_state", table_name="restaurants")
    op.drop_index("ix_restaurants_postal_code", table_name="restaurants")
    op.drop_index("ix_restaurants_name", table_name="restaurants")
    op.drop_index("ix_restaurants_location", table_name="restaurants")
    op.drop_index("ix_restaurants_city", table_name="restaurants")
    op.drop_table("restaurants")

