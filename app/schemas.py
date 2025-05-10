from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

# ----------------- POKEMON -----------------

class PokemonBase(BaseModel):
    name: str
    element: Optional[str] = None
    hp: Optional[int] = None
    attack: Optional[int] = None
    defense: Optional[int] = None
    special_attack: Optional[int] = None
    special_defense: Optional[int] = None
    speed: Optional[int] = None
    moves: Optional[List[str]] = None
    current_hp: Optional[int] = None

class PokemonCreate(PokemonBase):
    pass

class Pokemon(PokemonBase):
    id: int

    class Config:
        orm_mode = True

# ----------------- TRAINER -----------------

class TrainerBase(BaseModel):
    name: str
    email: EmailStr
    level: Optional[int] = 1

class TrainerCreate(TrainerBase):
    pass

class Trainer(TrainerBase):
    id: int

    class Config:
        orm_mode = True

# ----------------- TRAINER POKEMON -----------------

class TrainerPokemonBase(BaseModel):
    trainer_id: int
    pokemon_id: int
    is_shiny: bool = False

class TrainerPokemonCreate(TrainerPokemonBase):
    pass

class TrainerPokemon(TrainerPokemonBase):
    class Config:
        orm_mode = True

# ----------------- BATTLES -----------------

class BattleBase(BaseModel):
    trainer_id: int
    opponent_name: str
    winner: Optional[str] = None
    date: Optional[str] = None

class BattleCreate(BaseModel):
    trainer_id: int
    opponent_id: int

class BattleUpdate(BaseModel):
    winner: Optional[str] = None
    date: Optional[str] = None

class Battle(BattleBase):
    id: int
    trainer_name: Optional[str] = None  # Nuevo campo para mostrar nombre

    class Config:
        orm_mode = True

class BattlePokemonBase(BaseModel):
    battle_id: int
    pokemon_id: int
    hp_remaining: int
    participated: bool = False

class BattlePokemonCreate(BattlePokemonBase):
    pass

class BattlePokemon(BattlePokemonBase):
    id: int
    pokemon: Optional[Pokemon] = None

    class Config:
        orm_mode = True

class BattleWithPokemon(Battle):
    pokemons: List[BattlePokemon] = []

    class Config:
        orm_mode = True

# ----------------- RESULTADO DETALLADO DE BATALLA -----------------

class BattleResult(BaseModel):
    battle_id: int
    winner_id: Optional[int] = None
    winner_name: str
    loser_name: str
    trainer_pokemon: Pokemon
    opponent_pokemon: Pokemon
    trainer_hp_remaining: int
    opponent_hp_remaining: int
    battle_log: List[str]

# ----------------- PARA REFERENCIAS CIRCULARES -----------------

BattleWithPokemon.update_forward_refs()