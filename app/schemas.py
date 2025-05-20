# Importaciones necesarias
from typing import List, Optional
from pydantic import BaseModel, EmailStr  # BaseModel para esquemas, EmailStr para validación de email

class AdminBase(BaseModel):
    username: str
    email: EmailStr

class AdminCreate(AdminBase):
    password: str

class Admin(AdminBase):
    id: int
    is_active: bool
    is_superadmin: bool

    class Config:
        from_attributes = True

class AdminInDB(Admin):
    hashed_password: str

## ------------------------- ESQUEMAS PARA POKÉMON ------------------------- ##

class PokemonBase(BaseModel):
    """
    Esquema base para Pokémon con todos los atributos comunes.
    Todos los campos excepto 'name' son opcionales para mayor flexibilidad.
    """
    name: str  # Nombre del Pokémon (requerido)
    element: Optional[str] = None  # Tipo elemental (Agua, Fuego, etc.)
    hp: Optional[int] = None  # Puntos de salud base
    attack: Optional[int] = None  # Ataque físico
    defense: Optional[int] = None  # Defensa física
    special_attack: Optional[int] = None  # Ataque especial
    special_defense: Optional[int] = None  # Defensa especial
    speed: Optional[int] = None  # Velocidad en combate
    moves: Optional[List[str]] = None  # Lista de movimientos disponibles
    current_hp: Optional[int] = None  # HP actual (para combates)
    level: Optional[int] = 1  # Nivel del Pokémon (nuevo campo con valor por defecto 1)

class PokemonCreate(PokemonBase):
    """
    Esquema para creación de Pokémon. Hereda todos los campos de PokemonBase.
    Podría incluir validaciones adicionales específicas para creación.
    """
    pass

class Pokemon(PokemonBase):
    """
    Esquema para representación completa de Pokémon, incluyendo ID.
    Se usa para respuestas API cuando se necesita mostrar un Pokémon.
    """
    id: int  # ID único del Pokémon en la base de datos

    class Config:
        orm_mode = True  # Permite la conversión automática desde ORM de SQLAlchemy
        
class PokemonUpdate(BaseModel):
    current_hp: int | None = None
    level: int | None = None
    # Agrega aquí otros campos que necesites actualizar
## ------------------------- ESQUEMAS PARA ENTRENADORES ------------------------- ##

class TrainerBase(BaseModel):
    """
    Esquema base para Entrenadores Pokémon.
    """
    name: str  # Nombre del entrenador (requerido)
    email: EmailStr  # Email con validación automática de formato
    level: Optional[int] = 1  # Nivel del entrenador (default 1)

class TrainerCreate(TrainerBase):
    """
    Esquema para creación de entrenadores. 
    Hereda los campos de TrainerBase.
    """
    pass

class Trainer(TrainerBase):
    """
    Esquema completo de entrenador para respuestas API.
    Incluye el ID generado por la base de datos.
    """
    id: int  # ID único del entrenador

    class Config:
        orm_mode = True  # Habilita compatibilidad con ORM

## ------------------------- ESQUEMAS PARA RELACIÓN ENTRENADOR-POKÉMON ------------------------- ##

class TrainerPokemonBase(BaseModel):
    """
    Esquema base para la relación entre entrenadores y Pokémon.
    Representa qué Pokémon pertenecen a qué entrenador.
    """
    trainer_id: int  # ID del entrenador dueño
    pokemon_id: int  # ID del Pokémon en la colección
    is_shiny: bool = False  # Indica si es una variante shiny (default False)

class TrainerPokemonCreate(TrainerPokemonBase):
    """
    Esquema para crear nuevas relaciones entrenador-pokémon.
    """
    pass

class TrainerPokemon(TrainerPokemonBase):
    """
    Esquema completo de la relación, útil para respuestas API.
    """
    class Config:
        orm_mode = True  # Compatibilidad con ORM

## ------------------------- ESQUEMAS PARA BATALLAS ------------------------- ##

class BattleBase(BaseModel):
    """
    Esquema base para batallas Pokémon.
    """
    trainer_id: int  # ID del entrenador que inicia la batalla
    opponent_id: int  # ID del entrenador oponente
    winner: Optional[str] = None  # Nombre del ganador (se establece al terminar)
    date: Optional[str] = None  # Fecha de la batalla (auto-generada)

class BattleCreate(BaseModel):
    """
    Esquema para iniciar una nueva batalla.
    Solo necesita los IDs de los participantes.
    """
    trainer_id: int
    opponent_id: int

class BattleUpdate(BaseModel):
    """
    Esquema para actualizar una batalla existente.
    Solo campos que pueden modificarse después de creada.
    """
    winner: Optional[str] = None  # Para establecer el ganador
    date: Optional[str] = None  # Fecha personalizada (raro pero posible)

class Battle(BattleBase):
    """
    Esquema completo de batalla para respuestas API.
    Incluye información extendida como nombres de participantes.
    """
    id: int  # ID único de la batalla
    trainer_name: Optional[str] = None  # Nombre del entrenador (para mostrar)
    opponent_name: Optional[str] = None  # Nombre del oponente (para mostrar)

    class Config:
        orm_mode = True  # Compatibilidad con ORM

class BattlePokemonBase(BaseModel):
    """
    Esquema base para Pokémon participantes en batallas.
    Lleva registro del estado durante la batalla.
    """
    battle_id: int  # ID de la batalla
    pokemon_id: int  # ID del Pokémon
    hp_remaining: int  # HP actual durante la batalla
    participated: bool = False  # Si participó efectivamente

class BattlePokemonCreate(BattlePokemonBase):
    """
    Esquema para agregar Pokémon a una batalla.
    """
    pass

class BattlePokemon(BattlePokemonBase):
    """
    Esquema completo de Pokémon en batalla para respuestas API.
    Incluye los datos completos del Pokémon asociado.
    """
    id: int  # ID de esta relación
    pokemon: Optional[Pokemon] = None  # Datos completos del Pokémon

    class Config:
        orm_mode = True  # Compatibilidad con ORM

class BattleWithPokemon(Battle):
    """
    Esquema extendido de batalla que incluye lista de Pokémon participantes.
    Útil para mostrar todos los detalles de una batalla en una sola respuesta.
    """
    pokemons: List[BattlePokemon] = []  # Lista de Pokémon en la batalla

    class Config:
        orm_mode = True  # Compatibilidad con ORM

## ------------------------- RESULTADO DETALLADO DE BATALLA ------------------------- ##

class BattleResult(BaseModel):
    """
    Esquema para el resultado detallado de una batalla.
    Contiene información completa para mostrar el desarrollo del combate.
    """
    battle_id: int
    winner_id: Optional[int]
    winner_name: str
    loser_name: str
    trainer_pokemon: Pokemon
    opponent_pokemon: Pokemon
    trainer_hp_remaining: int
    opponent_hp_remaining: int
    battle_log: List[str]
    last_trainer_attack: Optional[str] = None  # Hacer opcional o proporcionar valor por defecto
    last_opponent_attack: Optional[str] = None
    trainer_wins: int
    opponent_wins: int
    is_best_of_three: bool
    keep_winner_pokemon: bool # Indica si se mantiene el Pokémon ganador para la siguiente batalla
## ------------------------- MANEJO DE REFERENCIAS CIRCULARES ------------------------- ##

# Resuelve referencias circulares entre esquemas que se referencian mutuamente
BattleWithPokemon.update_forward_refs()