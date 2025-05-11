from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import random
from .. import schemas, crud, models
from ..database import get_db

router = APIRouter(  
    tags=["Batallas"]  # Agrupación para la documentación Swagger/OpenAPI
)

# --------------------------------------------------
# SISTEMA DE TIPOS POKÉMON (EFECTIVIDADES)
# --------------------------------------------------

TYPE_ADVANTAGES = {
    # Efectividades (2x de daño)
    "Planta": {"Agua": 2.0, "Roca": 2.0, "Tierra": 2.0},
    "Fuego": {"Planta": 2.0, "Bicho": 2.0, "Hielo": 2.0, "Acero": 2.0},
    "Agua": {"Fuego": 2.0, "Roca": 2.0, "Tierra": 2.0},
    "Eléctrico": {"Agua": 2.0, "Volador": 2.0},
    "Hielo": {"Planta": 2.0, "Tierra": 2.0, "Volador": 2.0, "Dragón": 2.0},
    "Lucha": {"Normal": 2.0, "Hielo": 2.0, "Roca": 2.0, "Siniestro": 2.0, "Acero": 2.0},
    "Veneno": {"Planta": 2.0, "Hada": 2.0},
    "Tierra": {"Fuego": 2.0, "Eléctrico": 2.0, "Veneno": 2.0, "Roca": 2.0, "Acero": 2.0},
    "Volador": {"Planta": 2.0, "Lucha": 2.0, "Bicho": 2.0},
    "Psíquico": {"Lucha": 2.0, "Veneno": 2.0},
    "Bicho": {"Planta": 2.0, "Psíquico": 2.0, "Siniestro": 2.0},
    "Roca": {"Fuego": 2.0, "Hielo": 2.0, "Volador": 2.0, "Bicho": 2.0},
    "Fantasma": {"Psíquico": 2.0, "Fantasma": 2.0},
    "Dragón": {"Dragón": 2.0},
    "Siniestro": {"Psíquico": 2.0, "Fantasma": 2.0},
    "Acero": {"Hielo": 2.0, "Roca": 2.0, "Hada": 2.0},
    "Hada": {"Lucha": 2.0, "Dragón": 2.0, "Siniestro": 2.0},
    
    # Debilidades (0.5x de daño)
    "Planta": {"Fuego": 0.5, "Volador": 0.5, "Bicho": 0.5, "Hielo": 0.5, "Veneno": 0.5},
    "Fuego": {"Agua": 0.5, "Roca": 0.5, "Tierra": 0.5},
    "Agua": {"Eléctrico": 0.5, "Planta": 0.5},
    "Eléctrico": {"Tierra": 0.5},
    "Hielo": {"Fuego": 0.5, "Lucha": 0.5, "Roca": 0.5, "Acero": 0.5},
    "Lucha": {"Volador": 0.5, "Psíquico": 0.5, "Hada": 0.5},
    "Veneno": {"Tierra": 0.5, "Psíquico": 0.5},
    "Tierra": {"Agua": 0.5, "Planta": 0.5, "Hielo": 0.5},
    "Volador": {"Eléctrico": 0.5, "Hielo": 0.5, "Roca": 0.5},
    "Psíquico": {"Bicho": 0.5, "Fantasma": 0.5, "Siniestro": 0.5},
    "Bicho": {"Fuego": 0.5, "Volador": 0.5, "Roca": 0.5},
    "Roca": {"Agua": 0.5, "Planta": 0.5, "Lucha": 0.5, "Tierra": 0.5, "Acero": 0.5},
    "Fantasma": {"Fantasma": 0.5, "Siniestro": 0.5},
    "Dragón": {"Acero": 0.5},
    "Siniestro": {"Lucha": 0.5, "Bicho": 0.5, "Hada": 0.5},
    "Acero": {"Fuego": 0.5, "Lucha": 0.5, "Tierra": 0.5},
    "Hada": {"Veneno": 0.5, "Acero": 0.5}
}

def get_type_multiplier(attacker_type: str, defender_type: str) -> float:
    """Calcula el multiplicador de daño basado en los tipos"""
    multiplier = 1.0
    attacker_types = attacker_type.split("/")
    defender_types = defender_type.split("/")
    
    for atk_type in attacker_types:
        for def_type in defender_types:
            if atk_type in TYPE_ADVANTAGES and def_type in TYPE_ADVANTAGES[atk_type]:
                multiplier *= TYPE_ADVANTAGES[atk_type][def_type]
    
    return multiplier

# --------------------------------------------------
# MECÁNICAS DE COMBATE
# --------------------------------------------------

def get_random_attack(pokemon: schemas.Pokemon) -> str:
    """Obtiene un ataque aleatorio de los movimientos del Pokémon"""
    if pokemon.moves and len(pokemon.moves) > 0:
        return random.choice(pokemon.moves)
    return random.choice(["Placaje", "Arañazo", "Gruñido"])

def calculate_damage(attacker: schemas.Pokemon, defender: schemas.Pokemon, attack_used: str) -> int:
    """
    Calcula el daño de un ataque considerando:
    - Ataque/Defensa base
    - Ventaja de tipo
    - Aleatoriedad
    """
    # Daño base con variación aleatoria
    base_damage = random.randint(5, attacker.attack or 15)
    
    # Reducción por defensa
    defense_factor = max(1, (defender.defense or 10) / 10)
    
    # Multiplicador por tipo
    type_multiplier = get_type_multiplier(attacker.element or "Normal", defender.element or "Normal")
    
    # Daño final
    damage = max(1, int((base_damage * type_multiplier) / defense_factor))
    
    # Ataques especiales tienen bonus
    if "especial" in attack_used.lower():
        damage = int(damage * 1.2)
    
    return damage

# --------------------------------------------------
# SIMULACIÓN DE BATALLA
# --------------------------------------------------

async def simulate_battle(
    db: AsyncSession, 
    trainer_id: int, 
    opponent_id: int
) -> schemas.BattleResult:
    """
    Simula una batalla Pokémon completa entre dos entrenadores
    con mecánicas de turnos, tipos y daño.
    """
    # Validación de entrenadores
    trainer = await crud.get_trainer(db, trainer_id)
    opponent = await crud.get_trainer(db, opponent_id)
    
    if not trainer or not opponent:
        raise HTTPException(status_code=404, detail="Entrenador no encontrado")
    
    # Validación de equipos Pokémon
    trainer_pokemons = await crud.get_trainer_pokemons(db, trainer_id)
    opponent_pokemons = await crud.get_trainer_pokemons(db, opponent_id)
    
    if not trainer_pokemons or not opponent_pokemons:
        raise HTTPException(
            status_code=400, 
            detail="Ambos entrenadores necesitan Pokémon para pelear"
        )
    
    # Selección aleatoria de Pokémon
    trainer_pokemon = random.choice(trainer_pokemons).pokemon
    opponent_pokemon = random.choice(opponent_pokemons).pokemon
    
    # Inicialización de HP
    trainer_hp = trainer_pokemon.current_hp or trainer_pokemon.hp or 100
    opponent_hp = opponent_pokemon.current_hp or opponent_pokemon.hp or 100
    
    # Registro de batalla
    battle_log = []
    last_trainer_attack = ""
    last_opponent_attack = ""
    
    # Sistema de turnos
    while trainer_hp > 0 and opponent_hp > 0:
        # Turno del entrenador
        last_trainer_attack = get_random_attack(trainer_pokemon)
        damage = calculate_damage(trainer_pokemon, opponent_pokemon, last_trainer_attack)
        opponent_hp -= damage
        
        type_multiplier = get_type_multiplier(
            trainer_pokemon.element or "Normal", 
            opponent_pokemon.element or "Normal"
        )
        
        type_message = ""
        if type_multiplier > 1.5:
            type_message = " ¡Es muy efectivo!"
        elif type_multiplier < 0.5:
            type_message = " ¡No es muy efectivo..."
        
        battle_log.append(
            f"{trainer.name}: {trainer_pokemon.name} usa {last_trainer_attack} "
            f"contra {opponent_pokemon.name} (-{damage} HP){type_message}"
        )
        
        if opponent_hp <= 0:
            battle_log.append(f"¡{opponent_pokemon.name} se debilitó!")
            break
            
        # Turno del oponente
        last_opponent_attack = get_random_attack(opponent_pokemon)
        damage = calculate_damage(opponent_pokemon, trainer_pokemon, last_opponent_attack)
        trainer_hp -= damage
        
        type_multiplier = get_type_multiplier(
            opponent_pokemon.element or "Normal", 
            trainer_pokemon.element or "Normal"
        )
        
        type_message = ""
        if type_multiplier > 1.5:
            type_message = " ¡Es muy efectivo!"
        elif type_multiplier < 0.5:
            type_message = " ¡No es muy efectivo..."
        
        battle_log.append(
            f"{opponent.name}: {opponent_pokemon.name} usa {last_opponent_attack} "
            f"contra {trainer_pokemon.name} (-{damage} HP){type_message}"
        )
        
        if trainer_hp <= 0:
            battle_log.append(f"¡{trainer_pokemon.name} se debilitó!")
    
    # Determinación del ganador
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

    # Registro en base de datos
    battle_data = schemas.BattleCreate(
        trainer_id=trainer_id,
        opponent_id=opponent_id
    )
    
    db_battle = await crud.create_battle(db, battle_data)
    
    # Actualización con resultado
    if winner_name != "Empate":
        await crud.update_battle(
            db, 
            db_battle.id, 
            schemas.BattleUpdate(
                winner=winner_name,
                date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )
    
    # Registro de Pokémon participantes
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
    
    # Resultado detallado
    return schemas.BattleResult(
        battle_id=db_battle.id,
        winner_id=winner_id,
        winner_name=winner_name,
        loser_name=loser_name,
        trainer_pokemon=trainer_pokemon,
        opponent_pokemon=opponent_pokemon,
        trainer_hp_remaining=max(0, trainer_hp),
        opponent_hp_remaining=max(0, opponent_hp),
        battle_log=battle_log,
        last_trainer_attack=last_trainer_attack,
        last_opponent_attack=last_opponent_attack
    )

# --------------------------------------------------
# ENDPOINTS DE LA API
# --------------------------------------------------

@router.post("/", response_model=schemas.BattleResult)
async def create_battle(
    battle: schemas.BattleCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Inicia una nueva batalla entre dos entrenadores"""
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
    """Obtiene los detalles completos de una batalla específica"""
    db_battle = await crud.get_battle_with_pokemons(db, battle_id)
    if db_battle is None:
        raise HTTPException(status_code=404, detail="Batalla no encontrada")
    
    # Asegurar nombres de entrenadores
    if not hasattr(db_battle, 'trainer_name'):
        trainer = await crud.get_trainer(db, db_battle.trainer_id)
        db_battle.trainer_name = trainer.name if trainer else "Desconocido"
    
    if not hasattr(db_battle, 'opponent_name'):
        opponent = await crud.get_trainer(db, db_battle.opponent_id)
        db_battle.opponent_name = opponent.name if opponent else "Desconocido"
    
    return db_battle

@router.get("/", response_model=List[schemas.Battle])
async def read_battles(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene un listado paginado de todas las batallas registradas"""
    battles = await crud.get_battles(db, skip=skip, limit=limit)
    
    # Asegurar nombres de entrenadores
    for battle in battles:
        if not hasattr(battle, 'trainer_name'):
            trainer = await crud.get_trainer(db, battle.trainer_id)
            battle.trainer_name = trainer.name if trainer else "Desconocido"
        if not hasattr(battle, 'opponent_name'):
            opponent = await crud.get_trainer(db, battle.opponent_id)
            battle.opponent_name = opponent.name if opponent else "Desconocido"
    
    return battles