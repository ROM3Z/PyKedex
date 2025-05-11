from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from typing import List, Optional

from .. import models, schemas, crud
from ..database import get_db

router = APIRouter(
    tags=["Pokémon"]    # Agrupación para la documentación Swagger/OpenAPI
)

@router.post("/", response_model=schemas.Pokemon)
async def create_pokemon(
    pokemon: schemas.PokemonCreate, 
    db: AsyncSession = Depends(get_db)
):
    return await crud.create_pokemon(db, pokemon)

@router.get("/", response_model=List[schemas.Pokemon])
async def read_pokemons(
    skip: int = 0, 
    limit: int = 10,
    name: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    pokemons = await crud.get_pokemons(db, skip=skip, limit=limit, name=name)
    return pokemons

@router.get("/search/", response_model=List[schemas.Pokemon])
async def search_pokemons_by_name(
    name: str,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Búsqueda avanzada por nombre con coincidencias aproximadas.
    - Case insensitive
    - Coincidencias parciales
    - Ordena por mejor coincidencia primero
    Ejemplo: /search/?name=pika encontrará "Pikachu", "Pikachu Gigamax", etc.
    """
    pokemons = await crud.search_pokemons_by_name(db, name=name, skip=skip, limit=limit)
    if not pokemons:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron Pokémon con nombre similar a '{name}'"
        )
    return pokemons

@router.get("/flexible-search/", response_model=List[schemas.Pokemon])
async def flexible_pokemon_search(
    search_term: str,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Búsqueda flexible que intenta encontrar coincidencias incluso con pequeños errores
    """
    pokemons = await crud.flexible_pokemon_search(db, search_term=search_term, skip=skip, limit=limit)
    if not pokemons:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron Pokémon para el término '{search_term}'"
        )
    return pokemons

@router.get("/{pokemon_id}", response_model=schemas.Pokemon)
async def read_pokemon(
    pokemon_id: int, 
    db: AsyncSession = Depends(get_db)
):
    db_pokemon = await crud.get_pokemon(db, pokemon_id=pokemon_id)
    if db_pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon no encontrado")
    return db_pokemon

@router.put("/{pokemon_id}", response_model=schemas.Pokemon)
async def update_pokemon(
    pokemon_id: int, 
    pokemon: schemas.PokemonCreate, 
    db: AsyncSession = Depends(get_db)
):
    db_pokemon = await crud.update_pokemon(db, pokemon_id, pokemon)
    if db_pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon no encontrado")
    return db_pokemon

@router.delete("/{pokemon_id}", response_model=schemas.Pokemon)
async def delete_pokemon(
    pokemon_id: int, 
    db: AsyncSession = Depends(get_db)
):
    db_pokemon = await crud.delete_pokemon(db, pokemon_id)
    if db_pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon no encontrado")
    return db_pokemon