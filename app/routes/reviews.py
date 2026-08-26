from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import FoodItem, Review, User
from app.schemas import ReviewCreate, ReviewRead, ReviewUpdate

router = APIRouter(tags=["reviews"])


PageParam = Annotated[int, Query(ge=1)]
LimitParam = Annotated[int, Query(ge=1, le=100)]


def update_food_item_rating_stats(db: Session, food_item_id: int) -> None:
    count, average = db.execute(
        select(func.count(Review.id), func.avg(Review.rating)).where(Review.food_item_id == food_item_id)
    ).one()
    food_item = db.get(FoodItem, food_item_id)
    if food_item is None:
        return
    food_item.review_count = count
    food_item.average_rating = Decimal("0.00") if average is None else Decimal(str(average)).quantize(Decimal("0.01"))


@router.get("/food-items/{food_item_id}/reviews", response_model=list[ReviewRead])
def list_food_item_reviews(
    food_item_id: int,
    db: Annotated[Session, Depends(get_db)],
    page: PageParam = 1,
    limit: LimitParam = 20,
) -> list[Review]:
    food_item = db.get(FoodItem, food_item_id)
    if food_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")

    offset = (page - 1) * limit
    statement = (
        select(Review)
        .where(Review.food_item_id == food_item_id)
        .order_by(Review.created_at.desc(), Review.id.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(statement))


@router.post("/food-items/{food_item_id}/reviews", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
def create_review(
    food_item_id: int,
    payload: ReviewCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Review:
    food_item = db.get(FoodItem, food_item_id)
    if food_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")

    review = Review(food_item_id=food_item_id, user_id=current_user.id, **payload.model_dump())
    db.add(review)
    try:
        db.flush()
        update_food_item_rating_stats(db, food_item_id)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User has already reviewed this food item",
        ) from exc

    db.refresh(review)
    return review


@router.get("/reviews/{review_id}", response_model=ReviewRead)
def get_review(review_id: int, db: Annotated[Session, Depends(get_db)]) -> Review:
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return review


@router.patch("/reviews/{review_id}", response_model=ReviewRead)
def update_review(
    review_id: int,
    payload: ReviewUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Review:
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    if review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to modify this review")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)

    db.flush()
    update_food_item_rating_stats(db, review.food_item_id)
    db.commit()
    db.refresh(review)
    return review


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Response:
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    if review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete this review")

    food_item_id = review.food_item_id
    db.delete(review)
    db.flush()
    update_food_item_rating_stats(db, food_item_id)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
