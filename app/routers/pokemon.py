from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, or_
from typing import List, Optional
from difflib import get_close_matches

from app.schemas import Admin
from app.routers.auth import get_current_superadmin, get_current_admin

import unicodedata
import re

from .. import models, schemas, crud
from ..database import get_db

router = APIRouter(
    tags=["Pokémon"]    # Agrupación para la documentación Swagger/OpenAPI
)

# --------------------------------------------------
# FUNCIONES AUXILIARES PARA BÚSQUEDA INTELIGENTE
# --------------------------------------------------

def normalize_text(text: str) -> str:
    """
    Normaliza texto para búsquedas:
    - Convierte a minúsculas
    - Elimina acentos y caracteres especiales
    - Elimina espacios extras
    """
    text = text.lower().strip()
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    return re.sub(r'\s+', ' ', text)

def find_similar_names(search_term: str, names: List[str], threshold: float = 0.6) -> List[str]:
    """
    Encuentra nombres similares usando coincidencia aproximada.
    
    Args:
        search_term: Término de búsqueda
        names: Lista de nombres disponibles
        threshold: Umbral de similitud (0-1)
        
    Returns:
        Lista de nombres que superan el umbral de similitud
    """
    normalized_search = normalize_text(search_term)
    normalized_names = [normalize_text(name) for name in names]
    
    matches = get_close_matches(
        normalized_search,
        normalized_names,
        n=5,
        cutoff=threshold
    )
    
    # Recuperar los nombres originales
    original_matches = []
    for match in matches:
        index = normalized_names.index(match)
        original_matches.append(names[index])
    
    return original_matches

# --------------------------------------------------
# ENDPOINTS
# --------------------------------------------------

@router.post("/", response_model=schemas.Pokemon)
async def create_pokemon(
    pokemon: schemas.PokemonCreate, 
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Crea un nuevo Pokémon en la base de datos.
    
    Args:
        pokemon: Datos del Pokémon a crear
        db: Sesión de base de datos
        
    Returns:
        El Pokémon creado con su ID asignado
    """
    return await crud.create_pokemon(db, pokemon)

@router.get("/", response_model=List[schemas.Pokemon])
async def read_pokemons(
    name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Obtiene un listado paginado de Pokémon.
    
    Args:
        skip: Número de registros a omitir (paginación)
        limit: Máximo número de registros a devolver
        name: Filtro opcional por nombre (búsqueda exacta)
        db: Sesión de base de datos
        
    Returns:
        Lista de Pokémon paginados
    """
    pokemons = await crud.get_pokemons(db,name=name)
    return pokemons

@router.get("/search/", response_model=List[schemas.Pokemon])
async def search_pokemons_by_name(
    name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Búsqueda avanzada por nombre con coincidencias aproximadas.
    
    Características:
    - Case insensitive
    - Coincidencias parciales
    - Ordena por mejor coincidencia primero
    
    Args:
        name: Término de búsqueda (ej: "pika")
        skip: Número de registros a omitir
        limit: Máximo número de resultados
        db: Sesión de base de datos
        
    Returns:
        Lista de Pokémon que coinciden con el criterio
        
    Example:
        GET /pokemon/search/?name=pika
        Encontrará "Pikachu", "Pikachu Gigamax", etc.
    """
    pokemons = await crud.search_pokemons_by_name(db, name=name)
    if not pokemons:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron Pokémon con nombre similar a '{name}'"
        )
    return pokemons

@router.get("/flexible-search/", response_model=List[schemas.Pokemon])
async def flexible_pokemon_search(
    search_term: str,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Búsqueda inteligente con tolerancia a errores ortográficos.
    
    Implementa un sistema de 3 capas:
    1. Búsqueda exacta (case insensitive)
    2. Coincidencia aproximada (difflib)
    3. Búsqueda por subcadena
    
    Args:
        search_term: Término a buscar (ej: "picachu")
        skip: Registros a omitir
        limit: Máximo resultados
        db: Sesión de base de datos
        
    Returns:
        Lista de Pokémon ordenados por relevancia
        
    Example:
        GET /pokemon/flexible-search/?search_term=picachu
        Encontrará "Pikachu" aunque esté mal escrito
    """
    # Capa 1: Búsqueda exacta
    exact_match = await crud.get_pokemon_by_name(db, search_term)
    if exact_match:
        return [exact_match]
    
    # Capa 2: Coincidencia aproximada
    all_pokemons = await crud.get_pokemons(db,)
    all_names = [p.name for p in all_pokemons]
    
    similar_names = find_similar_names(search_term, all_names)
    if similar_names:
        pokemons = await crud.get_pokemons_by_names(db, similar_names)
        if pokemons:
            return pokemons
    
    # Capa 3: Búsqueda por subcadena
    pokemons = await crud.search_pokemons_by_name(db, name=search_term)
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
    """
    Obtiene un Pokémon específico por su ID.
    
    Args:
        pokemon_id: ID del Pokémon
        db: Sesión de base de datos
        
    Returns:
        Los datos completos del Pokémon
        
    Raises:
        HTTPException: 404 si no se encuentra
    """
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
    """
    Actualiza los datos de un Pokémon existente.
    
    Args:
        pokemon_id: ID del Pokémon a actualizar
        pokemon: Nuevos datos
        db: Sesión de base de datos
        
    Returns:
        Pokémon actualizado
        
    Raises:
        HTTPException: 404 si no se encuentra
    """
    db_pokemon = await crud.update_pokemon(db, pokemon_id, pokemon)
    if db_pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon no encontrado")
    return db_pokemon

@router.delete("/{pokemon_id}", response_model=schemas.Pokemon)
async def delete_pokemon(
    pokemon_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina un Pokémon de la base de datos.
    
    Args:
        pokemon_id: ID del Pokémon a eliminar
        db: Sesión de base de datos
        
    Returns:
        Pokémon eliminado
        
    Raises:
        HTTPException: 404 si no se encuentra
    """
    db_pokemon = await crud.delete_pokemon(db, pokemon_id)
    if db_pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon no encontrado")
    return db_pokemon