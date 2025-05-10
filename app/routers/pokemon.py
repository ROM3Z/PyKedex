from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .. import models, schemas, crud
from ..database import get_db

router = APIRouter(
    prefix="/pokemons",
    tags=["pokemons"]
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
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    pokemons = await crud.get_pokemons(db, skip=skip, limit=limit)
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