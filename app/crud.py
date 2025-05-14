# Importaciones de SQLAlchemy para operaciones asíncronas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_
from sqlalchemy.orm import selectinload, joinedload
from datetime import datetime, timezone
from typing import List, Optional

# Importaciones de SQLAlchemy para operaciones síncronas
from sqlalchemy.orm import Session
from app.models import Admin
from app.schemas import AdminCreate
from app.routers.auth import get_password_hash

# Importaciones de nuestros módulos internos
from . import schemas  # Esquemas Pydantic para validación de datos
from . import models  # Modelos de la base de datos

# Funciones CRUD para administradores
async def get_admin_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(Admin).where(Admin.username == username))
    return result.scalars().first()

async def create_admin(db: AsyncSession, admin_data: dict):
    db_admin = Admin(**admin_data)
    db.add(db_admin)
    await db.commit()
    await db.refresh(db_admin)
    return db_admin


# Función auxiliar para parsear movimientos de Pokémon
def parse_moves(moves):
    """
    Convierte una cadena de movimientos en formato "{move1,move2,...}" a una lista.
    
    Args:
        moves: Puede ser una cadena con formato especial o una lista.
        
    Returns:
        Lista de movimientos limpios.
    """
    if isinstance(moves, str):
        cleaned = moves.strip("{}").replace('\"', '"').split(',')
        return [m.strip().strip('"') for m in cleaned if m.strip()]
    return moves

## ------------------------- CRUD para Pokémon ------------------------- ##

async def get_pokemon(db: AsyncSession, pokemon_id: int):
    """
    Obtiene un Pokémon por su ID.
    
    Args:
        db: Sesión de base de datos asíncrona.
        pokemon_id: ID del Pokémon a buscar.
        
    Returns:
        El Pokémon encontrado o None si no existe.
    """
    result = await db.execute(
        select(models.Pokemon)
        .where(models.Pokemon.id == pokemon_id)
    )
    return result.scalar_one_or_none()

async def get_pokemons(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 10,
    name: Optional[str] = None
):
    """
    Obtiene una lista paginada de Pokémon con opción de filtrado por nombre.
    
    Args:
        db: Sesión de base de datos.
        skip: Número de registros a saltar (paginación).
        limit: Máximo número de registros a devolver.
        name: Filtro opcional por nombre (búsqueda parcial case insensitive).
        
    Returns:
        Lista de Pokémon.
    """
    query = select(models.Pokemon)
    
    if name:
        query = query.where(
            func.lower(models.Pokemon.name).contains(func.lower(name)))
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_pokemon_by_name(db: AsyncSession, name: str):
    """Busca un Pokémon por nombre exacto (case insensitive)"""
    result = await db.execute(
        select(models.Pokemon)
        .where(func.lower(models.Pokemon.name) == func.lower(name))
    )
    return result.scalars().first()

async def get_pokemons_by_names(db: AsyncSession, names: List[str], skip: int = 0, limit: int = 10):
    """Busca Pokémon por lista de nombres exactos"""
    result = await db.execute(
        select(models.Pokemon)
        .where(models.Pokemon.name.in_(names))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def search_pokemons_by_name(
    db: AsyncSession,
    name: str,
    skip: int = 0,
    limit: int = 10
) -> List[models.Pokemon]:
    """
    Búsqueda avanzada por nombre con:
    - Coincidencias parciales en cualquier parte del nombre
    - Case insensitive
    - Ordenamiento por mejor coincidencia
    
    Args:
        db: Sesión de base de datos.
        name: Término de búsqueda.
        skip: Registros a saltar.
        limit: Máximo de resultados.
        
    Returns:
        Lista de Pokémon ordenados por relevancia.
    """
    query = (
        select(models.Pokemon)
        .where(
            or_(
                func.lower(models.Pokemon.name).contains(func.lower(name)),
                models.Pokemon.name.ilike(f"%{name}%")
            )
        )
        .order_by(
            # Primero los que empiezan con el término de búsqueda
            func.lower(models.Pokemon.name).startswith(func.lower(name)).desc(),
            # Luego por longitud del nombre (más corto primero)
            func.length(models.Pokemon.name)
        )
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    return result.scalars().all()

async def create_pokemon(db: AsyncSession, pokemon: schemas.PokemonCreate):
    """
    Crea un nuevo Pokémon en la base de datos.
    
    Args:
        db: Sesión de base de datos.
        pokemon: Datos del Pokémon a crear.
        
    Returns:
        El Pokémon creado con su ID asignado.
    """
    data = pokemon.dict()
    data["moves"] = parse_moves(data.get("moves"))
    db_pokemon = models.Pokemon(**data)
    db.add(db_pokemon)
    await db.commit()
    await db.refresh(db_pokemon)
    return db_pokemon

async def update_pokemon(
    db: AsyncSession, 
    pokemon_id: int, 
    pokemon: schemas.PokemonCreate
):
    """
    Actualiza los datos de un Pokémon existente.
    
    Args:
        db: Sesión de base de datos.
        pokemon_id: ID del Pokémon a actualizar.
        pokemon: Nuevos datos del Pokémon.
        
    Returns:
        El Pokémon actualizado o None si no existe.
    """
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
    """
    Elimina un Pokémon de la base de datos.
    
    Args:
        db: Sesión de base de datos.
        pokemon_id: ID del Pokémon a eliminar.
        
    Returns:
        El Pokémon eliminado o None si no existe.
    """
    db_pokemon = await get_pokemon(db, pokemon_id)
    if db_pokemon:
        await db.delete(db_pokemon)
        await db.commit()
    return db_pokemon

async def flexible_pokemon_search(
    db: AsyncSession,
    search_term: str,
    skip: int = 0,
    limit: int = 10
) -> List[models.Pokemon]:
    """
    Búsqueda flexible que intenta encontrar coincidencias incluso con pequeños errores.
    Primero intenta búsqueda exacta, luego parcial si no hay resultados.
    
    Args:
        db: Sesión de base de datos.
        search_term: Término de búsqueda.
        skip: Registros a saltar.
        limit: Máximo de resultados.
        
    Returns:
        Lista de Pokémon que coinciden con el término.
    """
    # Primero intenta búsqueda exacta
    exact_match = await db.execute(
        select(models.Pokemon)
        .where(func.lower(models.Pokemon.name) == func.lower(search_term))
    )
    exact_match = exact_match.scalars().first()
    
    if exact_match:
        return [exact_match]
    
    # Si no hay coincidencia exacta, busca coincidencias parciales
    return await search_pokemons_by_name(db, search_term, skip, limit)

## ------------------------- CRUD para Entrenadores ------------------------- ##

async def get_trainer(db: AsyncSession, trainer_id: int):
    """
    Obtiene un entrenador por su ID.
    
    Args:
        db: Sesión de base de datos.
        trainer_id: ID del entrenador.
        
    Returns:
        El entrenador encontrado o None si no existe.
    """
    result = await db.execute(
        select(models.Trainer)
        .where(models.Trainer.id == trainer_id)
    )
    return result.scalar_one_or_none()

async def get_trainers(db: AsyncSession, skip: int = 0, limit: int = 10):
    """
    Obtiene una lista paginada de entrenadores.
    
    Args:
        db: Sesión de base de datos.
        skip: Registros a saltar.
        limit: Máximo de resultados.
        
    Returns:
        Lista de entrenadores.
    """
    result = await db.execute(
        select(models.Trainer)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def create_trainer(db: AsyncSession, trainer: schemas.TrainerCreate):
    """
    Crea un nuevo entrenador.
    
    Args:
        db: Sesión de base de datos.
        trainer: Datos del entrenador.
        
    Returns:
        El entrenador creado con su ID asignado.
    """
    db_trainer = models.Trainer(**trainer.dict())
    db.add(db_trainer)
    await db.commit()
    await db.refresh(db_trainer)
    return db_trainer

async def update_trainer(
    db: AsyncSession, 
    trainer_id: int, 
    trainer: schemas.TrainerCreate
):
    """
    Actualiza los datos de un entrenador.
    
    Args:
        db: Sesión de base de datos.
        trainer_id: ID del entrenador.
        trainer: Nuevos datos del entrenador.
        
    Returns:
        El entrenador actualizado o None si no existe.
    """
    db_trainer = await get_trainer(db, trainer_id)
    if db_trainer:
        for key, value in trainer.dict().items():
            setattr(db_trainer, key, value)
        await db.commit()
        await db.refresh(db_trainer)
    return db_trainer

async def delete_trainer(db: AsyncSession, trainer_id: int):
    """
    Elimina un entrenador.
    
    Args:
        db: Sesión de base de datos.
        trainer_id: ID del entrenador.
        
    Returns:
        El entrenador eliminado o None si no existe.
    """
    db_trainer = await get_trainer(db, trainer_id)
    if db_trainer:
        await db.delete(db_trainer)
        await db.commit()
    return db_trainer

## ------------------------- Relación Pokémon-Entrenadores ------------------------- ##

async def add_pokemon_to_trainer(
    db: AsyncSession, 
    trainer_pokemon: schemas.TrainerPokemonCreate
):
    """
    Agrega un Pokémon a la colección de un entrenador.
    
    Args:
        db: Sesión de base de datos.
        trainer_pokemon: Datos de la relación.
        
    Returns:
        La relación creada.
    """
    db_trainer_pokemon = models.TrainerPokemon(**trainer_pokemon.dict())
    db.add(db_trainer_pokemon)
    await db.commit()
    await db.refresh(db_trainer_pokemon)
    return db_trainer_pokemon

async def get_trainer_pokemons(db: AsyncSession, trainer_id: int):
    """
    Obtiene todos los Pokémon de un entrenador específico.
    
    Args:
        db: Sesión de base de datos.
        trainer_id: ID del entrenador.
        
    Returns:
        Lista de Pokémon del entrenador.
    """
    result = await db.execute(
        select(models.TrainerPokemon)
        .where(models.TrainerPokemon.trainer_id == trainer_id)
        .options(selectinload(models.TrainerPokemon.pokemon))
    )
    return result.scalars().all()

async def remove_pokemon_from_trainer(
    db: AsyncSession, 
    trainer_id: int, 
    pokemon_id: int
):
    """
    Elimina un Pokémon de la colección de un entrenador.
    
    Args:
        db: Sesión de base de datos.
        trainer_id: ID del entrenador.
        pokemon_id: ID del Pokémon a remover.
        
    Returns:
        La relación eliminada o None si no existía.
    """
    result = await db.execute(
        select(models.TrainerPokemon)
        .where(
            models.TrainerPokemon.trainer_id == trainer_id,
            models.TrainerPokemon.pokemon_id == pokemon_id
        )
    )
    db_trainer_pokemon = result.scalar_one_or_none()
    if db_trainer_pokemon:
        await db.delete(db_trainer_pokemon)
        await db.commit()
    return db_trainer_pokemon

## ------------------------- Funciones de Batalla ------------------------- ##

async def update_pokemon_hp_remaining(
    db: AsyncSession, 
    pokemon_id: int, 
    battle_id: int, 
    hp_remaining: int
):
    """
    Actualiza los HP restantes de un Pokémon en una batalla específica.
    
    Args:
        db: Sesión de base de datos.
        pokemon_id: ID del Pokémon.
        battle_id: ID de la batalla.
        hp_remaining: Nuevo valor de HP.
        
    Returns:
        El registro actualizado o None si no existe.
    """
    result = await db.execute(
        select(models.BattlePokemon)
        .where(
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

## ------------------------- CRUD para Batallas ------------------------- ##

async def create_battle(db: AsyncSession, battle: schemas.BattleCreate):
    """
    Crea un nuevo registro de batalla.
    
    Args:
        db: Sesión de base de datos.
        battle: Datos de la batalla.
        
    Returns:
        La batalla creada.
        
    Raises:
        ValueError: Si algún entrenador no existe.
    """
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
    """
    Obtiene una batalla por su ID con información del entrenador.
    
    Args:
        db: Sesión de base de datos.
        battle_id: ID de la batalla.
        
    Returns:
        La batalla encontrada con datos extendidos o None.
    """
    result = await db.execute(
        select(models.Battle)
        .where(models.Battle.id == battle_id)
        .options(joinedload(models.Battle.trainer))
    )
    battle = result.scalar_one_or_none()
    
    if battle and hasattr(battle, 'trainer'):
        battle.trainer_name = battle.trainer.name
    
    return battle

async def get_battles(db: AsyncSession, skip: int = 0, limit: int = 10):
    """
    Obtiene una lista paginada de batallas con información extendida.
    
    Args:
        db: Sesión de base de datos.
        skip: Registros a saltar.
        limit: Máximo de resultados.
        
    Returns:
        Lista de batallas con datos extendidos.
    """
    result = await db.execute(
        select(models.Battle)
        .options(joinedload(models.Battle.trainer))
        .offset(skip)
        .limit(limit)
    )
    battles = result.scalars().all()
    
    for battle in battles:
        if not hasattr(battle, 'trainer_name') and hasattr(battle, 'trainer'):
            battle.trainer_name = battle.trainer.name
    
    return battles

async def update_battle(
    db: AsyncSession, 
    battle_id: int, 
    battle_update: schemas.BattleUpdate
):
    """
    Actualiza los datos de una batalla (como el ganador).
    
    Args:
        db: Sesión de base de datos.
        battle_id: ID de la batalla.
        battle_update: Datos a actualizar.
        
    Returns:
        La batalla actualizada o None si no existe.
    """
    db_battle = await get_battle(db, battle_id)
    if db_battle:
        for key, value in battle_update.dict(exclude_unset=True).items():
            setattr(db_battle, key, value)
        await db.commit()
        await db.refresh(db_battle)
    return db_battle

async def get_battle_with_pokemons(db: AsyncSession, battle_id: int):
    """
    Obtiene una batalla con todos los Pokémon participantes.
    
    Args:
        db: Sesión de base de datos.
        battle_id: ID de la batalla.
        
    Returns:
        La batalla con datos extendidos y lista de Pokémon o None.
    """
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

async def add_pokemon_to_battle(
    db: AsyncSession, 
    battle_pokemon: schemas.BattlePokemonCreate
):
    """
    Agrega un Pokémon a una batalla específica.
    
    Args:
        db: Sesión de base de datos.
        battle_pokemon: Datos de la relación.
        
    Returns:
        La relación creada.
    """
    db_battle_pokemon = models.BattlePokemon(**battle_pokemon.dict())
    db.add(db_battle_pokemon)
    await db.commit()
    await db.refresh(db_battle_pokemon)
    return db_battle_pokemon

async def get_battle_pokemons(db: AsyncSession, battle_id: int):
    """
    Obtiene todos los Pokémon participantes en una batalla.
    
    Args:
        db: Sesión de base de datos.
        battle_id: ID de la batalla.
        
    Returns:
        Lista de Pokémon en la batalla.
    """
    result = await db.execute(
        select(models.BattlePokemon)
        .where(models.BattlePokemon.battle_id == battle_id)
        .options(selectinload(models.BattlePokemon.pokemon))
    )
    return result.scalars().all()