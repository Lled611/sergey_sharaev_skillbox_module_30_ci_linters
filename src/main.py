from typing import List
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Path, Depends
from http import HTTPStatus
from sqlalchemy import select, Select, ScalarResult
from sqlalchemy.ext.asyncio.engine import AsyncConnection
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import exists

from .schemas import RecipeIn as SchemaRecipeIn, \
    RecipeOut as SchemaRecipeOut, \
    Ingredient as SchemaIngredient, \
    RecipeShortInfo as SchemaRecipeShortInfo, \
    ErrorDetail
from .database import engine, Base, get_session
from .models import Recipe, Product, Ingredient


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn: AsyncConnection
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
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
async def recipes(recipe_in: SchemaRecipeIn, session: AsyncSession = Depends(get_session)) -> None:
    stmt: Select = select(
        exists() \
            .where(Recipe.name == recipe_in.name)
        )

    if await session.scalar(stmt):
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
        stmt: Select = select(Product) \
            .where(Product.name == ingridient_in.product.name)

        product: Product = await session.scalar(stmt)
        if not product:
            product = Product(
                name=ingridient_in.product.name
            )

            session.add(product)
            await session.flush([product])

        ingridient: Ingredient = Ingredient(
            recipe_id=recipe.id,
            product_id=product.id,
            count=ingridient_in.count
        )

        session.add(ingridient)
    await session.commit()


@app.get(
    '/recipes',
    summary='Список всех рецептов',
    response_model=List[SchemaRecipeShortInfo]
)
async def recipes(session: AsyncSession = Depends(get_session)) -> List[Recipe]:
    '''
    Endpoint для получения списка всех рецептов.

    Рецепты отсортированы по количеству просмотров в порядке убывания.
    Если число просмотров совпадает, рецепты сортируются по времени приготовления.
    '''
    stmt: Select = select(Recipe) \
        .order_by(
            Recipe.views_count.desc(),
            Recipe.cooking_time,
            Recipe.id
        )

    result: ScalarResult = await session.scalars(stmt)

    return result.all()


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
    ), session: AsyncSession = Depends(get_session)
) -> SchemaRecipeOut:
    stmt: Select = select(Recipe) \
        .options(
            selectinload(Recipe.ingredients).selectinload(Ingredient.product)
        ) \
        .where(Recipe.id == recipe_id)

    recipe: Recipe = await session.scalar(stmt)

    if recipe:
        recipe.views_count += 1
        await session.commit()

        recipe_out = SchemaRecipeOut.model_validate(recipe)

        return recipe_out
    else:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f'Рецепта с id={recipe_id} не существует!'
        )
