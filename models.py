from __future__ import annotations
from typing import List
from sqlalchemy import Column, ForeignKey, Integer, String, select, Select, ScalarResult, Result, Row, and_
from sqlalchemy.orm import relationship, subqueryload, selectinload
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.sql import exists
from database import session, Base


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    ingredients = relationship(
        'Ingredient',
        backref='product',
        cascade='all'
    )

    # recipes = association_proxy(
    #     target_collection='ingredients',
    #     attr='recipe'
    # )

    def __str__(self) -> str:
        return self.name

    @classmethod
    async def get_or_create(cls, name) -> Product:
        stmt: Select = select(cls) \
            .where(cls.name == name)

        product: Product = await session.scalar(stmt)
        if not product:
            product = Product(
                name=name
            )

            session.add(product)
            await session.flush([product])

        return product


class Recipe(Base):
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    cooking_time = Column(Integer, nullable=False)
    views_count = Column(Integer, nullable=False, default=0)

    ingredients = relationship(
        'Ingredient',
        backref='recipe',
        cascade='all'
    )

    # products = association_proxy(
    #     target_collection='ingredients',
    #     attr='product'
    # )

    def __str__(self) -> str:
        return self.name

    @classmethod
    async def get_by_id(cls, id: int) -> Recipe | None:
        stmt: Select = select(cls) \
            .options(
                selectinload(cls.ingredients).selectinload(Ingredient.product)
            ) \
            .where(cls.id == id)

        return await session.scalar(stmt)

    @classmethod
    async def exists(cls, name: str) -> bool:
        stmt: Select = select(
            exists() \
                .where(cls.name == name)
        )

        return await session.scalar(stmt)

    @classmethod
    async def get_recipes(cls) -> List[Recipe]:
        stmt: Select = select(cls) \
            .order_by(
                cls.views_count.desc(),
                cls.cooking_time,
                cls.id
            )

        result: ScalarResult = await session.scalars(stmt)

        return result.all()

    def inc_views_count(self) -> None:
        self.views_count += 1


class Ingredient(Base):
    __tablename__ = 'ingredients'

    recipe_id = Column(Integer, ForeignKey('recipes.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    count = Column(Integer, nullable=False)
