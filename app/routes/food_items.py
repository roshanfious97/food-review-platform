from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FoodItem, Restaurant, User
from app.schemas import (
    FoodItemCreate,
    FoodItemRead,
    FoodItemWithRestaurantRead,
    normalize_food_item_name,
)

router = APIRouter(tags=["food-items"])


PageParam = Annotated[int, Query(ge=1)]
LimitParam = Annotated[int, Query(ge=1, le=100)]


@router.get("/restaurants/{restaurant_id}/food-items", response_model=list[FoodItemRead])
def list_restaurant_food_items(
    restaurant_id: int,
    db: Annotated[Session, Depends(get_db)],
    page: PageParam = 1,
    limit: LimitParam = 20,
) -> list[FoodItem]:
    restaurant = db.get(Restaurant, restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

    offset = (page - 1) * limit
    statement = (
        select(FoodItem)
        .where(FoodItem.restaurant_id == restaurant_id)
        .order_by(FoodItem.id)
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(statement))


@router.post("/restaurants/{restaurant_id}/food-items", response_model=FoodItemRead, status_code=status.HTTP_201_CREATED)
def create_food_item(
    restaurant_id: int,
    payload: FoodItemCreate,
    db: Annotated[Session, Depends(get_db)],
) -> FoodItem:
    restaurant = db.get(Restaurant, restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")

    if payload.created_by_user_id is not None and db.get(User, payload.created_by_user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    food_item = FoodItem(
        restaurant_id=restaurant_id,
        normalized_name=normalize_food_item_name(payload.name),
        **payload.model_dump(),
    )
    db.add(food_item)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Food item already exists for this restaurant",
        ) from exc

    db.refresh(food_item)
    return food_item

@router.get(
    "/food-items",
    response_model=list[FoodItemWithRestaurantRead],
)
def list_food_items(
    db: Annotated[Session, Depends(get_db)],
    page: PageParam = 1,
    limit: LimitParam = 20,
    search: str | None = None,
) -> list[FoodItem]:
    offset = (page - 1) * limit

    statement = select(FoodItem)

    if search:
        search_term = normalize_food_item_name(search)
        statement = statement.where(
            FoodItem.normalized_name.contains(search_term)
        )

    statement = (
        statement
        .options(joinedload(FoodItem.restaurant))
        .order_by(FoodItem.average_rating.desc(), FoodItem.id)
        .offset(offset)
        .limit(limit)
    )

    return list(db.scalars(statement))

@router.get(
    "/food-items/{food_item_id}",
    response_model=FoodItemWithRestaurantRead,
)
def get_food_item(
    food_item_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> FoodItem:
    food_item = db.scalar(
        select(FoodItem)
        .options(joinedload(FoodItem.restaurant))
        .where(FoodItem.id == food_item_id)
    )

    if food_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food item not found",
        )

    return food_item