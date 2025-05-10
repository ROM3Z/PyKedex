from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from sqlalchemy import DateTime
from .database import Base

class Pokemon(Base):
    __tablename__ = "pokemons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    element = Column(String(50))
    hp = Column(Integer)
    attack = Column(Integer)
    defense = Column(Integer)
    special_attack = Column(Integer)
    special_defense = Column(Integer)
    speed = Column(Integer)
    moves = Column(ARRAY(String))
    current_hp = Column(Integer)  # HP actual para batallas

    # Relación con TrainerPokemon (relación intermedia con Trainer)
    trainer_pokemons = relationship("TrainerPokemon", back_populates="pokemon")
    battles = relationship("BattlePokemon", back_populates="pokemon")


class Trainer(Base):
    __tablename__ = "trainers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    level = Column(Integer, default=1)

    # Relación con Pokémon a través de TrainerPokemon (tabla intermedia)
    pokemons = relationship("TrainerPokemon", back_populates="trainer")
    battles = relationship("Battle", back_populates="trainer")


class TrainerPokemon(Base):
    __tablename__ = "trainer_pokemons"

    trainer_id = Column(Integer, ForeignKey("trainers.id", ondelete="CASCADE"), primary_key=True)
    pokemon_id = Column(Integer, ForeignKey("pokemons.id", ondelete="CASCADE"), primary_key=True)
    is_shiny = Column(Boolean, default=False)

    # Relación con Pokémon y Trainer
    pokemon = relationship("Pokemon", back_populates="trainer_pokemons")
    trainer = relationship("Trainer", back_populates="pokemons")


class ShinyPokemon(Base):
    __tablename__ = "shiny_pokemons"

    id = Column(Integer, primary_key=True, index=True)
    pokemon_id = Column(Integer, ForeignKey("pokemons.id", ondelete="CASCADE"))


class Battle(Base):
    __tablename__ = "battles"

    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("trainers.id"))
    opponent_name = Column(String(100), nullable=False)
    winner = Column(String(100))  # Cambiado de winner_id a winner (string)
    date = Column(String, default=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))

    trainer = relationship("Trainer", back_populates="battles")
    pokemons = relationship("BattlePokemon", back_populates="battle")


class BattlePokemon(Base):
    __tablename__ = "battle_pokemons"

    id = Column(Integer, primary_key=True, index=True)
    battle_id = Column(Integer, ForeignKey("battles.id"))
    pokemon_id = Column(Integer, ForeignKey("pokemons.id"))
    hp_remaining = Column(Integer)
    participated = Column(Boolean, default=False)

    battle = relationship("Battle", back_populates="pokemons")
    pokemon = relationship("Pokemon", back_populates="battles")
