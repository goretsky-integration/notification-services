from datetime import datetime

from pydantic import BaseModel

__all__ = (
    'IngredientStop',
    'StopSalesByOtherIngredients',
)


class IngredientStop(BaseModel):
    started_at: datetime
    name: str
    reason: str


class StopSalesByOtherIngredients(BaseModel):
    unit_name: str
    ingredients: list[IngredientStop]
