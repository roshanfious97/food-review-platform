from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def normalize_food_item_name(value: str) -> str:
    return " ".join(value.casefold().strip().split())


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    display_name: str = Field(min_length=1, max_length=100)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not any(character.isalpha() for character in value):
            raise ValueError("Password must contain at least one letter")
        if not any(character.isdigit() for character in value):
            raise ValueError("Password must contain at least one number")
        return value


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RestaurantBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    address_line1: str = Field(min_length=1, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)
    country: str = Field(default="India", min_length=1, max_length=100)
    latitude: Decimal | None = Field(default=None, ge=Decimal("-90"), le=Decimal("90"))
    longitude: Decimal | None = Field(default=None, ge=Decimal("-180"), le=Decimal("180"))
    phone: str | None = Field(default=None, max_length=40)
    website_url: str | None = Field(default=None, max_length=500)


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantRead(RestaurantBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FoodItemBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    price: Decimal | None = Field(default=None, ge=Decimal("0"))
    currency: str = Field(default="INR", min_length=3, max_length=3)
    is_available: bool = True

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class FoodItemCreate(FoodItemBase):
    created_by_user_id: int | None = None


class FoodItemRead(FoodItemBase):
    id: int
    restaurant_id: int
    created_by_user_id: int | None
    normalized_name: str
    average_rating: Decimal
    review_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FoodItemRestaurantRead(BaseModel):
    id: int
    name: str
    city: str

    model_config = ConfigDict(from_attributes=True)


class FoodItemWithRestaurantRead(FoodItemRead):
    restaurant: FoodItemRestaurantRead


class ReviewBase(BaseModel):
    rating: int = Field(ge=1, le=5)
    body: str | None = Field(default=None, max_length=5000)
    would_order_again: bool | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ReviewCreate(ReviewBase):
    model_config = ConfigDict(extra="forbid")


class ReviewUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    body: str | None = Field(default=None, max_length=5000)
    would_order_again: bool | None = None


class ReviewRead(ReviewBase):
    id: int
    user_id: int
    food_item_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
