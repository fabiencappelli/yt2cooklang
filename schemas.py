from pydantic import BaseModel, Field
from typing import Optional, Any


class Ingredient(BaseModel):
    name: str
    quantity: Optional[float | str] = None
    unit: Optional[str] = None
    preparation: Optional[str] = None
    confidence: float = Field(default=0.8, ge=0, le=1)


class Cookware(BaseModel):
    name: str
    confidence: float = Field(default=0.8, ge=0, le=1)


class Timer(BaseModel):
    quantity: Optional[float | int | str] = None
    unit: Optional[str] = None


class Step(BaseModel):
    text: Optional[str] = None
    cooklang_text: str
    order: Optional[int] = None
    confidence: float = Field(default=0.8, ge=0, le=1)


class RecipeExtraction(BaseModel):
    title: str
    description: Optional[str] = None
    source: Optional[str] = None
    author: Optional[str] = None
    servings: Optional[str | int | float] = None
    cuisine: Optional[str] = None
    course: Optional[str] = None
    prep_time: Optional[str | int | float] = None
    cook_time: Optional[str | int | float] = None
    time_required: Optional[str | int | float] = None
    ingredients: list[Ingredient] = []
    cookware: list[Cookware] = []
    steps: list[Step]
    notes: list[str] = []
    uncertainties: list[str] = []