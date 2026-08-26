from fastapi import FastAPI

from app.config import get_settings
from app.routes import auth, food_items, health, restaurants, reviews


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(restaurants.router)
    app.include_router(food_items.router)
    app.include_router(reviews.router)
    return app


app = create_app()
