from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from sqlalchemy import DateTime
from .database import Base


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    is_superadmin = Column(Boolean, default=False)

class Pokemon(Base):
    """
    Modelo que representa un Pokémon en la base de datos.
    Contiene todos los atributos y estadísticas de un Pokémon.
    """
    __tablename__ = "pokemons"

    id = Column(Integer, primary_key=True, index=True)  # ID único
    name = Column(String(100), nullable=False)  # Nombre (requerido)
    element = Column(String(50))  # Tipo(s) elemental (ej: "Fuego/Volador")
    hp = Column(Integer)  # Puntos de salud base
    attack = Column(Integer)  # Ataque físico
    defense = Column(Integer)  # Defensa física
    special_attack = Column(Integer)  # Ataque especial
    special_defense = Column(Integer)  # Defensa especial
    speed = Column(Integer)  # Velocidad
    moves = Column(ARRAY(String))  # Lista de movimientos disponibles
    current_hp = Column(Integer)  # HP actual (para combates en curso)

    # Relación muchos-a-muchos con entrenadores (a través de TrainerPokemon)
    trainer_pokemons = relationship("TrainerPokemon", back_populates="pokemon")
    
    # Relación con las batallas en las que participó
    battles = relationship("BattlePokemon", back_populates="pokemon")

class Trainer(Base):
    """
    Modelo que representa un Entrenador Pokémon.
    Contiene la información básica del entrenador.
    """
    __tablename__ = "trainers"

    id = Column(Integer, primary_key=True, index=True)  # ID único
    name = Column(String(100), nullable=False)  # Nombre (requerido)
    email = Column(String(100), nullable=False, unique=True)  # Email (único)
    level = Column(Integer, default=1)  # Nivel (default 1)

    # Relación muchos-a-muchos con Pokémon (a través de TrainerPokemon)
    pokemons = relationship("TrainerPokemon", back_populates="trainer")
    
    # Relación con las batallas que ha participado
    battles = relationship("Battle", back_populates="trainer")

class TrainerPokemon(Base):
    """
    Modelo de relación muchos-a-muchos entre Entrenadores y Pokémon.
    Representa qué Pokémon pertenecen a qué entrenadores.
    """
    __tablename__ = "trainer_pokemons"

    # Clave primaria compuesta
    trainer_id = Column(
        Integer, 
        ForeignKey("trainers.id", ondelete="CASCADE"),  # Eliminación en cascada
        primary_key=True
    )
    pokemon_id = Column(
        Integer, 
        ForeignKey("pokemons.id", ondelete="CASCADE"),  # Eliminación en cascada
        primary_key=True
    )
    is_shiny = Column(Boolean, default=False)  # Indica si es una variante shiny

    # Relaciones con Pokémon y Entrenador
    pokemon = relationship("Pokemon", back_populates="trainer_pokemons")
    trainer = relationship("Trainer", back_populates="pokemons")

class ShinyPokemon(Base):
    """
    Modelo para registrar Pokémon shiny especiales.
    Puede usarse para llevar registro de shiny encontrados.
    """
    __tablename__ = "shiny_pokemons"

    id = Column(Integer, primary_key=True, index=True)  # ID único
    pokemon_id = Column(
        Integer, 
        ForeignKey("pokemons.id", ondelete="CASCADE")  # Eliminación en cascada
    )

class Battle(Base):
    """
    Modelo que representa una batalla Pokémon.
    Registra el resultado y participantes de cada combate.
    """
    __tablename__ = "battles"

    id = Column(Integer, primary_key=True, index=True)  # ID único
    trainer_id = Column(Integer, ForeignKey("trainers.id"))  # Entrenador que inició
    opponent_name = Column(String(100), nullable=False)  # Nombre del oponente
    winner = Column(String(100))  # Nombre del ganador (puede ser null para empates)
    date = Column(
        String, 
        default=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')  # Fecha auto-generada
    )

    # Relación con el entrenador que inició la batalla
    trainer = relationship("Trainer", back_populates="battles")
    
    # Relación con los Pokémon que participaron
    pokemons = relationship("BattlePokemon", back_populates="battle")

class BattlePokemon(Base):
    """
    Modelo de relación muchos-a-muchos entre Batallas y Pokémon.
    Registra qué Pokémon participaron en cada batalla y su estado.
    """
    __tablename__ = "battle_pokemons"

    id = Column(Integer, primary_key=True, index=True)  # ID único
    battle_id = Column(Integer, ForeignKey("battles.id"))  # ID de la batalla
    pokemon_id = Column(Integer, ForeignKey("pokemons.id"))  # ID del Pokémon
    hp_remaining = Column(Integer)  # HP restante al final de la batalla
    participated = Column(Boolean, default=False)  # Si participó efectivamente

    # Relaciones con Batalla y Pokémon
    battle = relationship("Battle", back_populates="pokemons")
    pokemon = relationship("Pokemon", back_populates="battles")