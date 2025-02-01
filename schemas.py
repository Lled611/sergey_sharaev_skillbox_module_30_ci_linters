from typing import List
from pydantic import BaseModel, Field, ConfigDict
from pydantic.dataclasses import dataclass


class Product(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(
        ...,
        title='Название продукта',
        description='Название продукта',
        min_length=2
    )

    # class Config:
    #     orm_mode=True


class Ingredient(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product: Product
    count: int = Field(
        ...,
        title='Количество продукта',
        description='Количество продукта',
        gt=0
    )

    # class Config:
    #     orm_mode=True


# @dataclass
class BaseRecipe(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(
        ...,
        title='Название рецепта',
        description='Название рецепта',
        min_length=2
    )
    description: str = Field(
        ...,
        title='Текстовое описание',
        description='Текстовое описание',
        min_length=2
    )
    cooking_time: int = Field(
        ...,
        title='Время готовки',
        description='Время готовки',
        gt=0
    )
    ingredients: List[Ingredient] = Field(
        ...,
        title='Список ингредиентов',
        description='Список ингредиентов',
        min_length=1
    )


# @dataclass
class RecipeIn(BaseRecipe):
    ...


# @dataclass
class RecipeOut(BaseRecipe):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        title='Id рецепта',
        description='Id рецепта'
    )

    # class Config:
    #     orm_mode=True


class RecipeShortInfo(BaseModel):
    id: int = Field(
        ...,
        title='Id рецепта',
        description='Id рецепта'
    )
    name: str = Field(
        ...,
        title='Название рецепта',
        description='Название рецепта'
    )
    views_count: int = Field(
        ...,
        title='Количество просмотров',
        description='Количество просмотров'
    )
    cooking_time: int = Field(
        ...,
        title='Время готовки',
        description='Время готовки'
    )

    class Config:
        orm_mode=True


class ErrorDetail(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            "example": {"detail": "HTTPException raised."},
        }
