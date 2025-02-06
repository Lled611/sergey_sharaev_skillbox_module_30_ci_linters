from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Path
from sqlalchemy import ScalarResult, Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.engine import AsyncConnection
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import exists

from .database import Base, engine, get_session
from .models import Ingredient, Product, Recipe
from .schemas import ErrorDetail
from .schemas import Ingredient as SchemaIngredient
from .schemas import RecipeIn as SchemaRecipeIn
from .schemas import RecipeOut as SchemaRecipeOut
from .schemas import RecipeShortInfo as SchemaRecipeShortInfo


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn: AsyncConnection
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Recipes", lifespan=lifespan)


@app.post(
    "/recipes",
    summary="Создать новый рецепт",
    description="Endpoint для добавления в базу новых рецептов",
    status_code=HTTPStatus.NO_CONTENT,
    responses={HTTPStatus.BAD_REQUEST: {"model": ErrorDetail}},
)
async def create_recipe(
    recipe_in: SchemaRecipeIn, session: AsyncSession = Depends(get_session)
) -> None:
    stmt: Select = select(exists().where(Recipe.name == recipe_in.name))

    if await session.scalar(stmt):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f'Рецепт "{recipe_in.name}" уже существует!',
        )

    recipe: Recipe = Recipe(
        name=recipe_in.name,
        description=recipe_in.description,
        cooking_time=recipe_in.cooking_time,
    )

    session.add(recipe)
    await session.flush([recipe])

    ingridient_in: SchemaIngredient
    for ingridient_in in recipe_in.ingredients:
        stmt = select(Product).where(Product.name == ingridient_in.product.name)

        product: Product = await session.scalar(stmt)
        if not product:
            product = Product(name=ingridient_in.product.name)

            session.add(product)
            await session.flush([product])

        ingridient: Ingredient = Ingredient(
            recipe_id=recipe.id, product_id=product.id, count=ingridient_in.count
        )

        session.add(ingridient)
    await session.commit()


@app.get(
    "/recipes",
    summary="Список всех рецептов",
    response_model=List[SchemaRecipeShortInfo],
)
async def recipes(session: AsyncSession = Depends(get_session)) -> List[Recipe]:
    """
    Endpoint для получения списка всех рецептов.

    Рецепты отсортированы по количеству просмотров в порядке убывания.
    Если число просмотров совпадает, рецепты сортируются по времени приготовления.
    """
    stmt: Select = select(Recipe).order_by(
        Recipe.views_count.desc(), Recipe.cooking_time, Recipe.id
    )

    result: ScalarResult = await session.scalars(stmt)

    return list(result.all())


@app.get(
    "/recipes/{recipe_id}",
    summary="Детальная информация о рецепте",
    description="Endpoint для получения детальной информации о рецепте",
    response_model=SchemaRecipeOut,
    responses={HTTPStatus.BAD_REQUEST: {"model": ErrorDetail}},
)
async def recipe_by_id(
    recipe_id: int = Path(..., title="Id рецепта", description="Id рецепта", gt=0),
    session: AsyncSession = Depends(get_session),
) -> SchemaRecipeOut:
    stmt: Select = (
        select(Recipe)
        .options(selectinload(Recipe.ingredients).selectinload(Ingredient.product))
        .where(Recipe.id == recipe_id)
    )

    recipe: Recipe = await session.scalar(stmt)

    if recipe:
        recipe.views_count += 1
        await session.commit()

        return SchemaRecipeOut.model_validate(recipe)
    else:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Рецепта с id={recipe_id} не существует!",
        )
