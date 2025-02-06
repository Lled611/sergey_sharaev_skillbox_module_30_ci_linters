from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    ingredients = relationship("Ingredient", backref="product", cascade="all")

    def __str__(self) -> str:
        return self.name


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    cooking_time = Column(Integer, nullable=False)
    views_count = Column(Integer, nullable=False, default=0)

    ingredients = relationship("Ingredient", backref="recipe", cascade="all")

    def __str__(self) -> str:
        return self.name


class Ingredient(Base):
    __tablename__ = "ingredients"

    recipe_id = Column(Integer, ForeignKey("recipes.id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    count = Column(Integer, nullable=False)
