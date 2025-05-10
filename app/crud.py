from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from datetime import datetime, timezone
from . import schemas
from . import models
from random import choice

def parse_moves(moves):
    if isinstance(moves, str):
        cleaned = moves.strip("{}").replace('\"', '"').split(',')
        return [m.strip().strip('"') for m in cleaned if m.strip()]
    return moves

# CRUD para Pokémon
async def get_pokemon(db: AsyncSession, pokemon_id: int):
    result = await db.execute(select(models.Pokemon).where(models.Pokemon.id == pokemon_id))
    return result.scalar_one_or_none()

async def get_pokemons(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Pokemon).offset(skip).limit(limit))
    return result.scalars().all()

async def create_pokemon(db: AsyncSession, pokemon: schemas.PokemonCreate):
    data = pokemon.dict()
    data["moves"] = parse_moves(data.get("moves"))
    db_pokemon = models.Pokemon(**data)
    db.add(db_pokemon)
    await db.commit()
    await db.refresh(db_pokemon)
    return db_pokemon

async def update_pokemon(db: AsyncSession, pokemon_id: int, pokemon: schemas.PokemonCreate):
    db_pokemon = await get_pokemon(db, pokemon_id)
    if db_pokemon:
        for key, value in pokemon.dict().items():
            if key == "moves":
                value = parse_moves(value)
            setattr(db_pokemon, key, value)
        await db.commit()
        await db.refresh(db_pokemon)
    return db_pokemon

async def delete_pokemon(db: AsyncSession, pokemon_id: int):
    db_pokemon = await get_pokemon(db, pokemon_id)
    if db_pokemon:
        await db.delete(db_pokemon)
        await db.commit()
    return db_pokemon

# CRUD para Entrenadores
async def get_trainer(db: AsyncSession, trainer_id: int):
    result = await db.execute(select(models.Trainer).where(models.Trainer.id == trainer_id))
    return result.scalar_one_or_none()

async def get_trainers(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Trainer).offset(skip).limit(limit))
    return result.scalars().all()

async def create_trainer(db: AsyncSession, trainer: schemas.TrainerCreate):
    db_trainer = models.Trainer(**trainer.dict())
    db.add(db_trainer)
    await db.commit()
    await db.refresh(db_trainer)
    return db_trainer

async def update_trainer(db: AsyncSession, trainer_id: int, trainer: schemas.TrainerCreate):
    db_trainer = await get_trainer(db, trainer_id)
    if db_trainer:
        for key, value in trainer.dict().items():
            setattr(db_trainer, key, value)
        await db.commit()
        await db.refresh(db_trainer)
    return db_trainer

async def delete_trainer(db: AsyncSession, trainer_id: int):
    db_trainer = await get_trainer(db, trainer_id)
    if db_trainer:
        await db.delete(db_trainer)
        await db.commit()
    return db_trainer

# Relación entre Pokémon y Entrenadores
async def add_pokemon_to_trainer(db: AsyncSession, trainer_pokemon: schemas.TrainerPokemonCreate):
    db_trainer_pokemon = models.TrainerPokemon(**trainer_pokemon.dict())
    db.add(db_trainer_pokemon)
    await db.commit()
    await db.refresh(db_trainer_pokemon)
    return db_trainer_pokemon

async def get_trainer_pokemons(db: AsyncSession, trainer_id: int):
    result = await db.execute(
        select(models.TrainerPokemon)
        .where(models.TrainerPokemon.trainer_id == trainer_id)
        .options(selectinload(models.TrainerPokemon.pokemon))
    )
    return result.scalars().all()

async def remove_pokemon_from_trainer(db: AsyncSession, trainer_id: int, pokemon_id: int):
    result = await db.execute(
        select(models.TrainerPokemon).where(
            models.TrainerPokemon.trainer_id == trainer_id,
            models.TrainerPokemon.pokemon_id == pokemon_id
        )
    )
    db_trainer_pokemon = result.scalar_one_or_none()
    if db_trainer_pokemon:
        await db.delete(db_trainer_pokemon)
        await db.commit()
    return db_trainer_pokemon

async def update_pokemon_hp_remaining(db: AsyncSession, pokemon_id: int, battle_id: int, hp_remaining: int):
    result = await db.execute(
        select(models.BattlePokemon).where(
            models.BattlePokemon.pokemon_id == pokemon_id,
            models.BattlePokemon.battle_id == battle_id
        )
    )
    db_battle_pokemon = result.scalar_one_or_none()

    if db_battle_pokemon:
        db_battle_pokemon.hp_remaining = hp_remaining
        await db.commit()
        await db.refresh(db_battle_pokemon)
        return db_battle_pokemon
    return None

# CRUD para Batallas
async def create_battle(db: AsyncSession, battle: schemas.BattleCreate):
    opponent = await get_trainer(db, battle.opponent_id)
    trainer = await get_trainer(db, battle.trainer_id)
    
    if not opponent or not trainer:
        raise ValueError("Entrenador no encontrado")

    db_battle = models.Battle(
        trainer_id=battle.trainer_id,
        opponent_name=opponent.name,
        winner=None,
        date=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    )
    
    db.add(db_battle)
    await db.commit()
    await db.refresh(db_battle)
    return db_battle

async def get_battle(db: AsyncSession, battle_id: int):
    result = await db.execute(
        select(models.Battle)
        .where(models.Battle.id == battle_id)
        .options(joinedload(models.Battle.trainer))
    )
    battle = result.scalar_one_or_none()
    
    if battle and hasattr(battle, 'trainer'):
        battle.trainer_name = battle.trainer.name
    
    return battle

async def get_battles(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.Battle)
        .options(joinedload(models.Battle.trainer))
        .offset(skip).limit(limit)
    )
    battles = result.scalars().all()
    
    # Asegurar que cada batalla tenga trainer_name
    for battle in battles:
        if not hasattr(battle, 'trainer_name') and hasattr(battle, 'trainer'):
            battle.trainer_name = battle.trainer.name
    
    return battles

async def update_battle(db: AsyncSession, battle_id: int, battle_update: schemas.BattleUpdate):
    db_battle = await get_battle(db, battle_id)
    if db_battle:
        for key, value in battle_update.dict(exclude_unset=True).items():
            setattr(db_battle, key, value)
        await db.commit()
        await db.refresh(db_battle)
    return db_battle

async def get_battle_with_pokemons(db: AsyncSession, battle_id: int):
    result = await db.execute(
        select(models.Battle)
        .where(models.Battle.id == battle_id)
        .options(
            joinedload(models.Battle.trainer),
            selectinload(models.Battle.pokemons).selectinload(models.BattlePokemon.pokemon)
        )
    )
    battle = result.scalar_one_or_none()
    
    if battle and hasattr(battle, 'trainer'):
        battle.trainer_name = battle.trainer.name
    
    return battle

async def add_pokemon_to_battle(db: AsyncSession, battle_pokemon: schemas.BattlePokemonCreate):
    db_battle_pokemon = models.BattlePokemon(**battle_pokemon.dict())
    db.add(db_battle_pokemon)
    await db.commit()
    await db.refresh(db_battle_pokemon)
    return db_battle_pokemon

async def get_battle_pokemons(db: AsyncSession, battle_id: int):
    result = await db.execute(
        select(models.BattlePokemon)
        .where(models.BattlePokemon.battle_id == battle_id)
        .options(selectinload(models.BattlePokemon.pokemon))
    )
    return result.scalars().all()