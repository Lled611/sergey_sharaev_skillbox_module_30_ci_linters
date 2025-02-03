from typing import List, Dict
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Path
from http import HTTPStatus
from sqlalchemy import Row, select
from sqlalchemy.ext.asyncio.engine import AsyncConnection
from sqlalchemy.orm import selectinload

from .schemas import RecipeIn as SchemaRecipeIn, \
    RecipeOut as SchemaRecipeOut, \
    Ingredient as SchemaIngredient, \
    RecipeShortInfo as SchemaRecipeShortInfo, \
    ErrorDetail
from .database import engine, session, Base
from .models import Recipe, Product, Ingredient


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn: AsyncConnection
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await session.close()
    await engine.dispose()


app = FastAPI(
    title='Recipes',
    lifespan=lifespan
)


@app.post(
    '/recipes',
    summary='Создать новый рецепт',
    description='Endpoint для добавления в базу новых рецептов',
    status_code=HTTPStatus.NO_CONTENT,
    responses={
        HTTPStatus.BAD_REQUEST: {
            'model': ErrorDetail
        }
    }
)
async def recipes(recipe_in: SchemaRecipeIn) -> None:
    async with session.begin():
        if await Recipe.exists(recipe_in.name):
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f'Рецепт "{recipe_in.name}" уже существует!'
            )

        recipe: Recipe = Recipe(
            name=recipe_in.name,
            description=recipe_in.description,
            cooking_time=recipe_in.cooking_time
        )

        session.add(recipe)
        await session.flush([recipe])

        ingridient_in: SchemaIngredient
        for ingridient_in in recipe_in.ingredients:
            product: Product = await Product.get_or_create(ingridient_in.product.name)

            ingridient: Ingredient = Ingredient(
                recipe_id=recipe.id,
                product_id=product.id,
                count=ingridient_in.count
            )

            session.add(ingridient)


@app.get(
    '/recipes',
    summary='Список всех рецептов',
    response_model=List[SchemaRecipeShortInfo]
)
async def recipes() -> List[Recipe]:
    '''
    Endpoint для получения списка всех рецептов.

    Рецепты отсортированы по количеству просмотров в порядке убывания.
    Если число просмотров совпадает, рецепты сортируются по времени приготовления.
    '''
    async with session.begin():
        return await Recipe.get_recipes()


@app.get(
    '/recipes/{recipe_id}',
    summary='Детальная информация о рецепте',
    description='Endpoint для получения детальной информации о рецепте',
    response_model=SchemaRecipeOut,
    responses={
        HTTPStatus.BAD_REQUEST: {
            'model': ErrorDetail
        }
    }
)
async def recipes(
    recipe_id: int = Path(
        ...,
        title='Id рецепта',
        description='Id рецепта',
        gt=0
    )
) -> SchemaRecipeOut:
    async with session.begin():
        recipe: Recipe = await Recipe.get_by_id(recipe_id)

        if recipe:
            print(isinstance(recipe, Recipe))

            recipe_out = SchemaRecipeOut.model_validate(recipe)

            print(isinstance(recipe_out, SchemaRecipeOut))

            return recipe_out
        else:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f'Рецепта с id={recipe_id} не существует!'
            )
