from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .. import schemas, crud
from ..database import get_db

router = APIRouter(
    prefix="/trainers",
    tags=["trainers"]
)

@router.post("/", response_model=schemas.Trainer)
async def create_trainer(
    trainer: schemas.TrainerCreate, 
    db: AsyncSession = Depends(get_db)
):
    return await crud.create_trainer(db, trainer)

@router.get("/", response_model=List[schemas.Trainer])
async def read_trainers(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    trainers = await crud.get_trainers(db, skip=skip, limit=limit)
    return trainers

@router.get("/{trainer_id}", response_model=schemas.Trainer)
async def read_trainer(
    trainer_id: int, 
    db: AsyncSession = Depends(get_db)
):
    db_trainer = await crud.get_trainer(db, trainer_id=trainer_id)
    if db_trainer is None:
        raise HTTPException(status_code=404, detail="Entrenador no encontrado")
    return db_trainer

@router.put("/{trainer_id}", response_model=schemas.Trainer)
async def update_trainer(
    trainer_id: int, 
    trainer: schemas.TrainerCreate, 
    db: AsyncSession = Depends(get_db)
):
    db_trainer = await crud.update_trainer(db, trainer_id, trainer)
    if db_trainer is None:
        raise HTTPException(status_code=404, detail="Entrenador no encontrado")
    return db_trainer

@router.delete("/{trainer_id}", response_model=schemas.Trainer)
async def delete_trainer(
    trainer_id: int, 
    db: AsyncSession = Depends(get_db)
):
    db_trainer = await crud.delete_trainer(db, trainer_id)
    if db_trainer is None:
        raise HTTPException(status_code=404, detail="Entrenador no encontrado")
    return db_trainer

@router.post("/{trainer_id}/pokemons", response_model=schemas.TrainerPokemon)
async def add_pokemon_to_trainer(
    trainer_id: int,
    pokemon_id: int,
    is_shiny: bool = False,
    db: AsyncSession = Depends(get_db)
):
    trainer_pokemon = schemas.TrainerPokemonCreate(
        trainer_id=trainer_id,
        pokemon_id=pokemon_id,
        is_shiny=is_shiny
    )
    return await crud.add_pokemon_to_trainer(db, trainer_pokemon)

@router.get("/{trainer_id}/pokemons", response_model=List[schemas.TrainerPokemon])
async def get_trainer_pokemons(
    trainer_id: int,
    db: AsyncSession = Depends(get_db)
):
    pokemons = await crud.get_trainer_pokemons(db, trainer_id)
    if not pokemons:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron Pokémon para este entrenador"
        )
    return pokemons