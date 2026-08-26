"""integer review ratings

Revision ID: 0002_integer_review_ratings
Revises: 0001_initial_models
Create Date: 2026-08-26 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_integer_review_ratings"
down_revision: Union[str, Sequence[str], None] = "0001_initial_models"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "reviews",
        "rating",
        existing_type=sa.Numeric(precision=2, scale=1),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="round(rating)::integer",
    )
    op.execute(
        """
        UPDATE food_items
        SET
            review_count = stats.review_count,
            average_rating = stats.average_rating
        FROM (
            SELECT
                food_items.id AS food_item_id,
                COUNT(reviews.id)::integer AS review_count,
                COALESCE(ROUND(AVG(reviews.rating)::numeric, 2), 0.00) AS average_rating
            FROM food_items
            LEFT JOIN reviews ON reviews.food_item_id = food_items.id
            GROUP BY food_items.id
        ) AS stats
        WHERE food_items.id = stats.food_item_id
        """
    )


def downgrade() -> None:
    op.alter_column(
        "reviews",
        "rating",
        existing_type=sa.Integer(),
        type_=sa.Numeric(precision=2, scale=1),
        existing_nullable=False,
        postgresql_using="rating::numeric(2,1)",
    )
    op.execute(
        """
        UPDATE food_items
        SET
            review_count = stats.review_count,
            average_rating = stats.average_rating
        FROM (
            SELECT
                food_items.id AS food_item_id,
                COUNT(reviews.id)::integer AS review_count,
                COALESCE(ROUND(AVG(reviews.rating)::numeric, 2), 0.00) AS average_rating
            FROM food_items
            LEFT JOIN reviews ON reviews.food_item_id = food_items.id
            GROUP BY food_items.id
        ) AS stats
        WHERE food_items.id = stats.food_item_id
        """
    )
