from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import random
from .. import schemas, crud, models
from ..database import get_db

router = APIRouter(
    prefix="/battles",
    tags=["battles"]
)

def calculate_damage(attacker: schemas.Pokemon, defender: schemas.Pokemon) -> int:
    """Calcula el daño considerando ataque y defensa"""
    base_damage = random.randint(1, attacker.attack or 10)
    defense_factor = max(1, (defender.defense or 10) / 100)
    return max(1, int(base_damage / defense_factor))

async def simulate_battle(
    db: AsyncSession, 
    trainer_id: int, 
    opponent_id: int
) -> schemas.BattleResult:
    # Verificar que los entrenadores existen
    trainer = await crud.get_trainer(db, trainer_id)
    opponent = await crud.get_trainer(db, opponent_id)
    
    if not trainer or not opponent:
        raise HTTPException(status_code=404, detail="Entrenador no encontrado")
    
    # Obtener los Pokémon de cada entrenador
    trainer_pokemons = await crud.get_trainer_pokemons(db, trainer_id)
    opponent_pokemons = await crud.get_trainer_pokemons(db, opponent_id)
    
    if not trainer_pokemons or not opponent_pokemons:
        raise HTTPException(
            status_code=400, 
            detail="Ambos entrenadores necesitan Pokémon para pelear"
        )
    
    # Seleccionar Pokémon aleatorio
    trainer_pokemon = random.choice(trainer_pokemons).pokemon
    opponent_pokemon = random.choice(opponent_pokemons).pokemon
    
    # Inicializar HP
    trainer_hp = trainer_pokemon.current_hp if trainer_pokemon.current_hp is not None else (trainer_pokemon.hp or 100)
    opponent_hp = opponent_pokemon.current_hp if opponent_pokemon.current_hp is not None else (opponent_pokemon.hp or 100)
    
    if trainer_hp <= 0 or opponent_hp <= 0:
        raise HTTPException(
            status_code=400,
            detail="Los Pokémon deben tener HP mayor que 0 para pelear"
        )
    
    # Simular batalla por turnos
    battle_log = []
    while trainer_hp > 0 and opponent_hp > 0:
        # Turno del entrenador
        damage = calculate_damage(trainer_pokemon, opponent_pokemon)
        opponent_hp -= damage
        battle_log.append(f"{trainer_pokemon.name} ataca a {opponent_pokemon.name} y causa {damage} de daño")
        
        if opponent_hp <= 0:
            battle_log.append(f"¡{opponent_pokemon.name} se debilitó!")
            break
            
        # Turno del oponente
        damage = calculate_damage(opponent_pokemon, trainer_pokemon)
        trainer_hp -= damage
        battle_log.append(f"{opponent_pokemon.name} ataca a {trainer_pokemon.name} y causa {damage} de daño")
        
        if trainer_hp <= 0:
            battle_log.append(f"¡{trainer_pokemon.name} se debilitó!")
    
    # Determinar resultados
    if trainer_hp > 0 and opponent_hp <= 0:
        winner_name = trainer.name
        winner_id = trainer.id
        loser_name = opponent.name
    elif opponent_hp > 0 and trainer_hp <= 0:
        winner_name = opponent.name
        winner_id = opponent.id
        loser_name = trainer.name
    else:
        winner_name = "Empate"
        winner_id = None
        loser_name = "Empate"

    # Crear registro de batalla
    battle_data = schemas.BattleCreate(
        trainer_id=trainer_id,
        opponent_id=opponent_id
    )
    
    db_battle = await crud.create_battle(db, battle_data)
    
    # Actualizar batalla con el resultado (excepto empates)
    if winner_name != "Empate":
        update_data = schemas.BattleUpdate(
            winner=winner_name,
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        db_battle = await crud.update_battle(db, db_battle.id, update_data)
    
    # Registrar Pokémon en la batalla
    await crud.add_pokemon_to_battle(
        db,
        schemas.BattlePokemonCreate(
            battle_id=db_battle.id,
            pokemon_id=trainer_pokemon.id,
            hp_remaining=max(0, trainer_hp),
            participated=True
        )
    )
    
    await crud.add_pokemon_to_battle(
        db,
        schemas.BattlePokemonCreate(
            battle_id=db_battle.id,
            pokemon_id=opponent_pokemon.id,
            hp_remaining=max(0, opponent_hp),
            participated=True
        )
    )
    
    return schemas.BattleResult(
        battle_id=db_battle.id,
        winner_id=winner_id,
        winner_name=winner_name,
        loser_name=loser_name,
        trainer_pokemon=trainer_pokemon,
        opponent_pokemon=opponent_pokemon,
        trainer_hp_remaining=max(0, trainer_hp),
        opponent_hp_remaining=max(0, opponent_hp),
        battle_log=battle_log
    )

@router.post("/", response_model=schemas.BattleResult)
async def create_battle(
    battle: schemas.BattleCreate, 
    db: AsyncSession = Depends(get_db)
):
    if battle.trainer_id == battle.opponent_id:
        raise HTTPException(
            status_code=400,
            detail="No puedes pelear contra ti mismo"
        )
    
    return await simulate_battle(db, battle.trainer_id, battle.opponent_id)

@router.get("/{battle_id}", response_model=schemas.BattleWithPokemon)
async def read_battle(
    battle_id: int,
    db: AsyncSession = Depends(get_db)
):
    db_battle = await crud.get_battle_with_pokemons(db, battle_id)
    if db_battle is None:
        raise HTTPException(status_code=404, detail="Batalla no encontrada")
    
    # Asegurar que trainer_name esté incluido
    if not hasattr(db_battle, 'trainer_name'):
        trainer = await crud.get_trainer(db, db_battle.trainer_id)
        db_battle.trainer_name = trainer.name if trainer else "Desconocido"
    
    return db_battle

@router.get("/", response_model=List[schemas.Battle])
async def read_battles(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    battles = await crud.get_battles(db, skip=skip, limit=limit)
    
    # Añadir trainer_name a cada batalla
    for battle in battles:
        if not hasattr(battle, 'trainer_name'):
            trainer = await crud.get_trainer(db, battle.trainer_id)
            battle.trainer_name = trainer.name if trainer else "Desconocido"
    
    return battles