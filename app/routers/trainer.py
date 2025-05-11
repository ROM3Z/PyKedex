# Importamos las bibliotecas necesarias
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

# Importamos los esquemas, operaciones CRUD y la conexión a la base de datos desde nuestros módulos
from .. import schemas, crud
from ..database import get_db

# Creamos un router de FastAPI para agrupar todas las rutas relacionadas con entrenadores
router = APIRouter(
    tags=["Entrenadores"]  # Agrupación para la documentación Swagger/OpenAPI
)

# Endpoint para crear un nuevo entrenador
@router.post("/", response_model=schemas.Trainer)
async def create_trainer(
    trainer: schemas.TrainerCreate,  # Datos del entrenador a crear (validados por el esquema)
    db: AsyncSession = Depends(get_db)  # Conexión a la base de datos (inyectada por FastAPI)
):
    """
    Crea un nuevo entrenador en la base de datos.
    
    Args:
        trainer: Datos del entrenador a crear.
        db: Sesión de base de datos asíncrona.
        
    Returns:
        El entrenador creado con su ID asignado.
    """
    return await crud.create_trainer(db, trainer)

# Endpoint para obtener una lista de entrenadores
@router.get("/", response_model=List[schemas.Trainer])
async def read_trainers(
    skip: int = 0,  # Número de registros a saltar (para paginación)
    limit: int = 10,  # Número máximo de registros a devolver (para paginación)
    db: AsyncSession = Depends(get_db)  # Conexión a la base de datos
):
    """
    Obtiene una lista de entrenadores con paginación.
    
    Args:
        skip: Número de entrenadores a saltar.
        limit: Número máximo de entrenadores a devolver.
        db: Sesión de base de datos asíncrona.
        
    Returns:
        Lista de entrenadores.
    """
    trainers = await crud.get_trainers(db, skip=skip, limit=limit)
    return trainers

# Endpoint para obtener un entrenador específico por su ID
@router.get("/{trainer_id}", response_model=schemas.Trainer)
async def read_trainer(
    trainer_id: int,  # ID del entrenador a buscar
    db: AsyncSession = Depends(get_db)  # Conexión a la base de datos
):
    """
    Obtiene un entrenador específico por su ID.
    
    Args:
        trainer_id: ID del entrenador a buscar.
        db: Sesión de base de datos asíncrona.
        
    Returns:
        Los datos del entrenador si existe.
        
    Raises:
        HTTPException: 404 si el entrenador no se encuentra.
    """
    db_trainer = await crud.get_trainer(db, trainer_id=trainer_id)
    if db_trainer is None:
        raise HTTPException(status_code=404, detail="Entrenador no encontrado")
    return db_trainer

# Endpoint para actualizar un entrenador existente
@router.put("/{trainer_id}", response_model=schemas.Trainer)
async def update_trainer(
    trainer_id: int,  # ID del entrenador a actualizar
    trainer: schemas.TrainerCreate,  # Nuevos datos del entrenador
    db: AsyncSession = Depends(get_db)  # Conexión a la base de datos
):
    """
    Actualiza los datos de un entrenador existente.
    
    Args:
        trainer_id: ID del entrenador a actualizar.
        trainer: Nuevos datos del entrenador.
        db: Sesión de base de datos asíncrona.
        
    Returns:
        Los datos actualizados del entrenador.
        
    Raises:
        HTTPException: 404 si el entrenador no se encuentra.
    """
    db_trainer = await crud.update_trainer(db, trainer_id, trainer)
    if db_trainer is None:
        raise HTTPException(status_code=404, detail="Entrenador no encontrado")
    return db_trainer

# Endpoint para eliminar un entrenador
@router.delete("/{trainer_id}", response_model=schemas.Trainer)
async def delete_trainer(
    trainer_id: int,  # ID del entrenador a eliminar
    db: AsyncSession = Depends(get_db)  # Conexión a la base de datos
):
    """
    Elimina un entrenador de la base de datos.
    
    Args:
        trainer_id: ID del entrenador a eliminar.
        db: Sesión de base de datos asíncrona.
        
    Returns:
        Los datos del entrenador eliminado.
        
    Raises:
        HTTPException: 404 si el entrenador no se encuentra.
    """
    db_trainer = await crud.delete_trainer(db, trainer_id)
    if db_trainer is None:
        raise HTTPException(status_code=404, detail="Entrenador no encontrado")
    return db_trainer

# Endpoint para agregar un Pokémon a un entrenador
@router.post("/{trainer_id}/pokemons", response_model=schemas.TrainerPokemon)
async def add_pokemon_to_trainer(
    trainer_id: int,  # ID del entrenador al que se agregará el Pokémon
    pokemon_id: int,  # ID del Pokémon a agregar
    is_shiny: bool = False,  # Indica si el Pokémon es shiny (opcional, default False)
    db: AsyncSession = Depends(get_db)  # Conexión a la base de datos
):
    """
    Agrega un Pokémon a la colección de un entrenador.
    
    Args:
        trainer_id: ID del entrenador.
        pokemon_id: ID del Pokémon a agregar.
        is_shiny: Si el Pokémon es shiny (opcional).
        db: Sesión de base de datos asíncrona.
        
    Returns:
        La relación entre el entrenador y el Pokémon creada.
    """
    # Creamos un objeto TrainerPokemonCreate con los datos recibidos
    trainer_pokemon = schemas.TrainerPokemonCreate(
        trainer_id=trainer_id,
        pokemon_id=pokemon_id,
        is_shiny=is_shiny
    )
    return await crud.add_pokemon_to_trainer(db, trainer_pokemon)

# Endpoint para obtener todos los Pokémon de un entrenador
@router.get("/{trainer_id}/pokemons", response_model=List[schemas.TrainerPokemon])
async def get_trainer_pokemons(
    trainer_id: int,  # ID del entrenador cuyos Pokémon queremos obtener
    db: AsyncSession = Depends(get_db)  # Conexión a la base de datos
):
    """
    Obtiene todos los Pokémon asociados a un entrenador.
    
    Args:
        trainer_id: ID del entrenador.
        db: Sesión de base de datos asíncrona.
        
    Returns:
        Lista de Pokémon del entrenador.
        
    Raises:
        HTTPException: 404 si el entrenador no tiene Pokémon o no existe.
    """
    pokemons = await crud.get_trainer_pokemons(db, trainer_id)
    if not pokemons:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron Pokémon para este entrenador"
        )
    return pokemons