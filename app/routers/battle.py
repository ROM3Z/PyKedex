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
# SISTEMA DE TIPOS POKÉMON (EFECTIVIDADES) Y FRASES
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

BATTLE_COMMENTS = [
    "¡El combate está muy reñido! Ambos Pokémon dan lo mejor de sí.",
    "¡Qué intensidad! Ningún Pokémon quiere ceder terreno.",
    "La batalla se prolonga... ¿Quién tendrá más resistencia?",
    "¡Increíble intercambio de golpes! Esto es digno de un campeonato.",
    "La estrategia de ambos entrenadores es impresionante.",
    "¡El público está al borde de sus asientos con esta batalla!",
    "Ninguno de los dos quiere perder, ¡esto es épico!",
    "¡Qué demostración de habilidad por ambos lados!",
    "La tensión es palpable en este enfrentamiento.",
    "¡Están igualados! Cualquier cosa puede pasar."
]

TRAINER_DIALOGUES = {
    "winning": [
        "¡Así se hace! Sigue así, {pokemon}!",
        "¡Perfecto! ¡Ese ataque fue directo!",
        "¡Vamos {pokemon}, tú puedes!",
        "¡Esa es la estrategia que practicamos!",
        "¡Excelente ejecución, {pokemon}!",
        "¡Justo como lo planeamos!",
        "¡No le des tregua, {pokemon}!"
    ],
    "losing": [
        "¡Aguanta {pokemon}, no te rindas!",
        "¡Contraataca ahora, {pokemon}!",
        "¡Cuidado con ese movimiento!",
        "¡No es momento de flaquear!",
        "¡Concéntrate, {pokemon}!",
        "¡Puedes superarlo, {pokemon}!",
        "¡No te dejes intimidar!"
    ],
    "critical": [
        "¡Sí! ¡Un golpe crítico!",
        "¡Directo al blanco! ¡Buen trabajo {pokemon}!",
        "¡Ese entrenamiento está dando frutos!",
        "¡Justo en el punto débil!",
        "¡Impacto perfecto, {pokemon}!"
    ],
    "resisted": [
        "¡Bien esquivado {pokemon}!",
        "¡Casi te alcanza! ¡Sigue así!",
        "¡Ese ataque no te afectará fácilmente!",
        "¡Buena defensa, {pokemon}!",
        "¡No tan rápido, rival!"
    ],
    "start": [
        "¡{pokemon}, yo te elijo!",
        "¡Es tu momento, {pokemon}!",
        "¡Confío en ti, {pokemon}!",
        "¡Hagámoslo, {pokemon}!",
        "¡A dar lo mejor, {pokemon}!"
    ],
    "x4_damage": [
        "¡Un golpe devastador! ¡Es muy efectivo!",
        "¡Impacto crítico! ¡El tipo es perfecto!",
        "¡{pokemon} es extremadamente vulnerable a este ataque!",
        "¡Golpe maestro! ¡El daño es enorme!",
        "¡{pokemon} no puede soportar este tipo de ataque!"
    ]
}

def get_type_multiplier(attacker_type: str, defender_type: str) -> float:
    """Calcula el multiplicador de daño basado en los tipos, incluyendo 4x de daño"""
    multiplier = 1.0
    attacker_types = attacker_type.split("/")
    defender_types = defender_type.split("/")

    for atk_type in attacker_types:
        for def_type in defender_types:
            if atk_type in TYPE_ADVANTAGES and def_type in TYPE_ADVANTAGES[atk_type]:
                multiplier *= TYPE_ADVANTAGES[atk_type][def_type]

    # Mensaje especial para daño 4x
    if multiplier >= 4.0:
        return multiplier
    elif multiplier <= 0.25:
        return multiplier
    else:
        return multiplier

# --------------------------------------------------
# MECÁNICAS DE COMBATE MEJORADAS CON NIVELES
# --------------------------------------------------

def get_random_attack(pokemon: schemas.Pokemon) -> str:
    """Obtiene un ataque aleatorio de los movimientos del Pokémon con 30% de probabilidad de ataque especial"""
    if pokemon.moves and len(pokemon.moves) > 0:
        if random.random() < 0.3 and hasattr(pokemon, 'special_attack'):
            return f"{random.choice(pokemon.moves)} (Especial)"
        return random.choice(pokemon.moves)
    return random.choice(["Placaje", "Arañazo", "Gruñido"])

def calculate_damage(
    attacker: schemas.Pokemon,
    defender: schemas.Pokemon,
    attack_used: str,
    attacker_level: int = 1,
    defender_level: int = 1
) -> tuple:
    """
    Calcula el daño de un ataque considerando:
    - Ataque/Defensa base o Ataque Especial/Defensa Especial
    - Ventaja de tipo (incluyendo 4x de daño)
    - Nivel del Pokémon
    - Aleatoriedad
    Retorna: (daño, es_crítico, es_especial, es_resistido)
    """
    # Determinar si es un ataque especial
    is_special = "especial" in attack_used.lower()

    # Daño base con variación aleatoria
    if is_special and hasattr(attacker, 'special_attack'):
        base_damage = random.randint(5, min(attacker.special_attack, 100) or 20)
        defense_stat = defender.special_defense if hasattr(defender, 'special_defense') else (defender.defense or 10)
    else:
        base_damage = random.randint(5, min(attacker.attack, 100) or 15)
        defense_stat = defender.defense or 10

    # Bonus por nivel del Pokémon (1-2% por nivel)
    attacker_level_bonus = 1 + (attacker_level * 0.02)
    base_damage = int(base_damage * attacker_level_bonus)

    # Reducción por defensa y nivel del defensor (1-1.5% por nivel)
    defense_level_reduction = max(1, defense_stat / (10 * (1 + defender_level * 0.015)))

    # Multiplicador por tipo (puede ser 4x o 0.25x)
    type_multiplier = get_type_multiplier(attacker.element or "Normal", defender.element or "Normal")

    # Daño final
    damage = max(1, int((base_damage * type_multiplier) / defense_level_reduction))

    # Bonus adicional por ataque especial
    if is_special:
        damage = int(damage * 1.3)  # 30% más de daño para ataques especiales

    # Posibilidad de golpe crítico (10% base + 0.1% por nivel del atacante)
    critical_chance = 0.1 + (attacker_level * 0.001)
    is_critical = random.random() < critical_chance
    if is_critical:
        damage = int(damage * 1.5)

    # Probabilidad de resistencia (0.1% por nivel del defensor)
    resist_chance = defender_level * 0.001
    if random.random() < resist_chance:
        damage = max(1, int(damage * 0.7))  # Reduce el daño en 30%
        return damage, is_critical, is_special, True  # Último parámetro indica resistencia

    return damage, is_critical, is_special, False

def determine_first_attacker(pokemon1: schemas.Pokemon, pokemon2: schemas.Pokemon) -> tuple:
    """
    Determina qué Pokémon ataca primero basado en la velocidad y nivel.
    Retorna: (attacker, defender, is_pokemon1_first)
    """
    # Velocidad base + 1% por nivel
    speed1 = (pokemon1.speed if hasattr(pokemon1, 'speed') and pokemon1.speed else 50) * (1 + (pokemon1.level if hasattr(pokemon1, 'level') else 1) * 0.01)
    speed2 = (pokemon2.speed if hasattr(pokemon2, 'speed') and pokemon2.speed else 50) * (1 + (pokemon2.level if hasattr(pokemon2, 'level') else 1) * 0.01)

    if speed1 == speed2:
        # Empate en velocidad, se decide al azar
        if random.random() < 0.5:
            return pokemon1, pokemon2, True
        else:
            return pokemon2, pokemon1, False
    elif speed1 > speed2:
        return pokemon1, pokemon2, True
    else:
        return pokemon2, pokemon1, False

def calculate_level_up(pokemon: schemas.Pokemon, battle_duration: int, is_winner: bool) -> int:
    """
    Calcula cuántos niveles sube un Pokémon después de una batalla
    - battle_duration: Número de turnos que duró la batalla
    - is_winner: Si el Pokémon ganó la batalla
    """
    if pokemon.level >= 100:  # Nivel máximo
        return 0

    base_exp = 10
    duration_bonus = min(battle_duration * 0.2, 20)  # Máximo 20 de bonus por duración
    winner_bonus = 15 if is_winner else 0

    total_exp = base_exp + duration_bonus + winner_bonus
    levels_gained = min(int(total_exp / 20), 2)  # Máximo 2 niveles por batalla

    return levels_gained

# --------------------------------------------------
# SIMULACIÓN DE BATALLA INDIVIDUAL (MEJORADA)
# --------------------------------------------------

async def simulate_single_battle(
    db: AsyncSession,
    trainer: schemas.Trainer,
    opponent: schemas.Trainer,
    trainer_pokemon: schemas.Pokemon,
    opponent_pokemon: schemas.Pokemon,
    previous_trainer_hp: Optional[int] = None
) -> dict:
    """
    Simula una sola batalla entre dos Pokémon con comentarios y diálogos mejorados.
    """
    # Inicialización de HP
    max_trainer_hp = trainer_pokemon.hp or 100
    max_opponent_hp = opponent_pokemon.hp or 100
    trainer_hp = previous_trainer_hp if previous_trainer_hp is not None else (trainer_pokemon.current_hp if trainer_pokemon.current_hp is not None else max_trainer_hp)
    opponent_hp = opponent_pokemon.current_hp if opponent_pokemon.current_hp is not None else max_opponent_hp

    # Obtener niveles de los Pokémon
    trainer_pokemon_level = trainer_pokemon.level if hasattr(trainer_pokemon, 'level') else 1
    opponent_pokemon_level = opponent_pokemon.level if hasattr(opponent_pokemon, 'level') else 1

    # Registro de batalla
    battle_log = []
    last_trainer_attack = ""
    last_opponent_attack = ""
    turn_count = 0

    # Diálogo inicial aleatorio
    trainer_dialogue = random.choice(TRAINER_DIALOGUES["start"]).format(pokemon=trainer_pokemon.name)
    opponent_dialogue = random.choice(TRAINER_DIALOGUES["start"]).format(pokemon=opponent_pokemon.name)
    battle_log.append(f"🗣️ {trainer.name}: {trainer_dialogue}")
    battle_log.append(f"🗣️ {opponent.name}: {opponent_dialogue}")

    # Determinar quién ataca primero
    first_attacker, first_defender, is_trainer_first = determine_first_attacker(
        trainer_pokemon, opponent_pokemon
    )

    # Mostrar velocidades
    speed1 = (trainer_pokemon.speed if hasattr(trainer_pokemon, 'speed') else 50)
    speed2 = (opponent_pokemon.speed if hasattr(opponent_pokemon, 'speed') else 50)
    
    battle_log.append(
        f"⚡ Velocidades: {trainer_pokemon.name} ({speed1}) vs {opponent_pokemon.name} ({speed2})"
    )

    battle_log.append(
        f"⚔️ ¡Comienza la batalla entre {trainer_pokemon.name} (Nv. {trainer_pokemon_level}, HP: {trainer_hp}/{max_trainer_hp}), "
        f"vs {opponent_pokemon.name} (Nv. {opponent_pokemon_level}, HP: {opponent_hp}/{max_opponent_hp})!"
    )

    if is_trainer_first:
        battle_log.append(f"⚡ ¡{trainer_pokemon.name} es más rápido y ataca primero!")
    else:
        battle_log.append(f"⚡ ¡{opponent_pokemon.name} es más rápido y ataca primero!")

    # Sistema de turnos
    while True:
        turn_count += 1

        # Comentario aleatorio cada 5 turnos
        if turn_count % 5 == 0 and turn_count > 0:
            battle_log.append(f"💬 {random.choice(BATTLE_COMMENTS)}")

        # Verificar si la batalla ha terminado
        if trainer_hp <= 0 or opponent_hp <= 0:
            break

        # Turno del primer atacante
        if is_trainer_first:
            attacker_name = trainer.name
            defender_name = opponent.name
            attacker_pokemon = trainer_pokemon
            defender_pokemon = opponent_pokemon
            attacker_level = trainer_pokemon_level
            defender_level = opponent_pokemon_level
        else:
            attacker_name = opponent.name
            defender_name = trainer.name
            attacker_pokemon = opponent_pokemon
            defender_pokemon = trainer_pokemon
            attacker_level = opponent_pokemon_level
            defender_level = trainer_pokemon_level

        # Diálogo aleatorio del entrenador (30% de probabilidad)
        if random.random() < 0.3:
            if (is_trainer_first and trainer_hp > opponent_hp) or (not is_trainer_first and opponent_hp > trainer_hp):
                dialogue_type = "winning"
            else:
                dialogue_type = "losing"
            
            dialogue = random.choice(TRAINER_DIALOGUES[dialogue_type]).format(pokemon=attacker_pokemon.name)
            battle_log.append(f"🗣️ {attacker_name}: {dialogue}")

        # Ataque
        attack_used = get_random_attack(attacker_pokemon)
        damage, is_critical, is_special, resisted = calculate_damage(
            attacker_pokemon,
            defender_pokemon,
            attack_used,
            attacker_level,
            defender_level
        )

        # Registrar el último ataque
        if is_trainer_first:
            last_trainer_attack = attack_used
        else:
            last_opponent_attack = attack_used

        # Multiplicador de tipo para mensajes especiales
        type_multiplier = get_type_multiplier(
            attacker_pokemon.element or "Normal",
            defender_pokemon.element or "Normal"
        )

        # Diálogo especial para daño 4x (50% de probabilidad)
        if type_multiplier >= 4.0 and random.random() < 0.5:
            dialogue = random.choice(TRAINER_DIALOGUES["x4_damage"]).format(pokemon=defender_pokemon.name)
            battle_log.append(f"🗣️ {attacker_name}: {dialogue}")

        # Diálogo para golpe crítico o resistencia (50% de probabilidad)
        if (is_critical or resisted) and random.random() < 0.5:
            dialogue_type = "critical" if is_critical else "resisted"
            dialogue = random.choice(TRAINER_DIALOGUES[dialogue_type]).format(pokemon=attacker_pokemon.name)
            battle_log.append(f"🗣️ {attacker_name}: {dialogue}")

        # Aplicar daño
        if is_trainer_first:
            opponent_hp -= damage
            opponent_hp = max(0, opponent_hp)  # No puede ser negativo
        else:
            trainer_hp -= damage
            trainer_hp = max(0, trainer_hp)

        # Mensajes de log
        type_message = ""
        if type_multiplier >= 4.0:
            type_message = " ¡Es extremadamente efectivo! (x4)"
        elif type_multiplier > 1.5:
            type_message = " ¡Es muy efectivo!"
        elif type_multiplier <= 0.25:
            type_message = " ¡Casi no afecta... (x0.25)"
        elif type_multiplier < 0.5:
            type_message = " ¡No es muy efectivo..."

        critical_message = " 💥¡Golpe crítico!" if is_critical else ""
        special_message = " ✨(Ataque especial)" if is_special else ""
        resist_message = " 🛡️¡Resistió el daño!" if resisted else ""

        # Determinar HP restante para mostrar
        if is_trainer_first:
            remaining_hp = opponent_hp
            max_hp = max_opponent_hp
            defender_pokemon_name = opponent_pokemon.name
        else:
            remaining_hp = trainer_hp
            max_hp = max_trainer_hp
            defender_pokemon_name = trainer_pokemon.name

        hp_percentage = (remaining_hp / max_hp) * 100
        hp_status = ""
        if hp_percentage > 60:
            hp_status = "🟢"
        elif hp_percentage > 30:
            hp_status = "🟡"
        else:
            hp_status = "🔴"

        battle_log.append(
            f"🔹 Turno {turn_count}: {attacker_pokemon.name} usa {attack_used}{special_message} "
            f"contra {defender_pokemon_name} -{damage} HP{type_message}{critical_message}{resist_message} "
            f"{hp_status} HP: {remaining_hp}/{max_hp}"
        )

        # Verificar si el defensor se debilitó
        if (is_trainer_first and opponent_hp <= 0) or (not is_trainer_first and trainer_hp <= 0):
            # 10% + 0.1% por nivel de probabilidad de un último ataque antes de debilitarse
            last_attack_chance = 0.1 + (defender_pokemon.level * 0.001)
            if random.random() < last_attack_chance:
                last_attack = get_random_attack(defender_pokemon)
                last_damage, last_critical, last_special, _ = calculate_damage(
                    defender_pokemon,
                    attacker_pokemon,
                    last_attack,
                    defender_level,
                    attacker_level
                )

                if is_trainer_first:
                    trainer_hp -= last_damage
                    trainer_hp = max(0, trainer_hp)
                else:
                    opponent_hp -= last_damage
                    opponent_hp = max(0, opponent_hp)

                last_critical_msg = " 💥¡Golpe crítico!" if last_critical else ""
                last_special_msg = " ✨(Ataque especial)" if last_special else ""

                battle_log.append(
                    f"🔥 ¡{defender_pokemon.name} contraataca con {last_attack}{last_special_msg} antes de debilitarse! "
                    f"-{last_damage} HP{last_critical_msg}"
                )

            battle_log.append(f"💀 ¡{defender_pokemon.name} se debilitó!")
            break

        # Cambiar turnos para el siguiente ataque
        is_trainer_first = not is_trainer_first

    # Determinar el ganador de esta batalla
    if trainer_hp > 0 and opponent_hp <= 0:
        winner = "trainer"
        winner_name = trainer.name
        winner_pokemon = trainer_pokemon
        loser_name = opponent.name
        loser_pokemon = opponent_pokemon
    elif opponent_hp > 0 and trainer_hp <= 0:
        winner = "opponent"
        winner_name = opponent.name
        winner_pokemon = opponent_pokemon
        loser_name = trainer.name
        loser_pokemon = trainer_pokemon
    else:
        winner = "draw"
        winner_name = "Empate"
        loser_name = "Empate"
        winner_pokemon = None
        loser_pokemon = None

    # Calcular subida de nivel para los Pokémon
    trainer_levels_gained = calculate_level_up(trainer_pokemon, turn_count, winner == "trainer")
    opponent_levels_gained = calculate_level_up(opponent_pokemon, turn_count, winner == "opponent")

    if trainer_levels_gained > 0:
        battle_log.append(f"🎉 ¡{trainer_pokemon.name} subió {trainer_levels_gained} nivel(es)! Ahora es nivel {trainer_pokemon_level + trainer_levels_gained}")
    if opponent_levels_gained > 0:
        battle_log.append(f"🎉 ¡{opponent_pokemon.name} subió {opponent_levels_gained} nivel(es)! Ahora es nivel {opponent_pokemon_level + opponent_levels_gained}")

    return {
        "winner": winner,
        "winner_name": winner_name,
        "loser_name": loser_name,
        "winner_pokemon": winner_pokemon,
        "loser_pokemon": loser_pokemon,
        "trainer_hp_remaining": max(0, trainer_hp),
        "opponent_hp_remaining": max(0, opponent_hp),
        "battle_log": battle_log,
        "trainer_pokemon": trainer_pokemon,
        "opponent_pokemon": opponent_pokemon,
        "last_trainer_attack": last_trainer_attack,
        "last_opponent_attack": last_opponent_attack,
        "turn_count": turn_count,
        "trainer_levels_gained": trainer_levels_gained,
        "opponent_levels_gained": opponent_levels_gained
    }

# --------------------------------------------------
# SIMULACIÓN DE BATALLA COMPLETA (MEJOR DE 3) CON MVP
# --------------------------------------------------

async def simulate_battle(
    db: AsyncSession,
    trainer_id: int,
    opponent_id: int,
    keep_winner_pokemon: bool = True,
    smart_selection: bool = True
) -> schemas.BattleResult:
    """
    Simula una batalla Pokémon completa entre dos entrenadores (mejor de 3)
    con comentarios mejorados, diálogos y resumen MVP.
    - keep_winner_pokemon: Si True, los Pokémon ganadores permanecen en batalla
    - smart_selection: Si True, los entrenadores eligen Pokémon estratégicamente
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

    # Registro de batalla general
    master_battle_log = []
    battle_results = []
    trainer_wins = 0
    opponent_wins = 0

    # Variables para mantener Pokémon ganadores entre batallas
    current_trainer_pokemon = None
    current_opponent_pokemon = None

    # Listas para Pokémon derrotados (no pueden volver a ser seleccionados)
    defeated_trainer_pokemons = set()
    defeated_opponent_pokemons = set()

    # Comentarista de la batalla
    commentator = "¡Esto fue épico! 🌟"

    # Mejor de 3 batallas
    for battle_num in range(1, 4):
        master_battle_log.append(f"🔥 BATALLA {battle_num} 🔥")

        # Función para selección inteligente de Pokémon
        def smart_pokemon_selection(pokemons, opponent_pokemon, defeated_pokemons, current_pokemon):
            """Selecciona el mejor Pokémon disponible contra el oponente"""
            available_pokemons = [
                p for p in pokemons 
                if p.pokemon.id not in defeated_pokemons and 
                (current_pokemon is None or p.pokemon.id != current_pokemon["pokemon"].id)
            ]
            
            if not available_pokemons:
                return None
                
            if opponent_pokemon:
                # Seleccionar Pokémon con ventaja de tipo
                best_pokemon = None
                best_score = -1
                
                for p in available_pokemons:
                    pokemon = p.pokemon
                    score = 0
                    
                    # Ventaja de tipo
                    type_multiplier = get_type_multiplier(pokemon.element or "Normal", opponent_pokemon.element or "Normal")
                    if type_multiplier >= 2.0:
                        score += 3
                    elif type_multiplier > 1.0:
                        score += 1
                    elif type_multiplier <= 0.5:
                        score -= 2
                        
                    # Estadísticas
                    score += (pokemon.attack or 0) / 10
                    score += (pokemon.special_attack or 0) / 10
                    score += (pokemon.speed or 0) / 20
                    
                    if score > best_score:
                        best_score = score
                        best_pokemon = pokemon
                        
                return best_pokemon if best_pokemon else random.choice(available_pokemons).pokemon
            else:
                # Primera batalla, seleccionar el más fuerte
                return max(available_pokemons, key=lambda x: (x.pokemon.attack or 0) + (x.pokemon.special_attack or 0)).pokemon

        # Selección de Pokémon para esta batalla
        if keep_winner_pokemon:
            # Para el entrenador
            if current_trainer_pokemon and current_trainer_pokemon.get("hp_remaining", 0) > 0:
                trainer_pokemon = current_trainer_pokemon["pokemon"]
                master_battle_log.append(f"⚡ {trainer.name} mantiene a {trainer_pokemon.name} en el campo! (HP: {current_trainer_pokemon['hp_remaining']}/{trainer_pokemon.hp})")
            else:
                if smart_selection:
                    opponent_current = current_opponent_pokemon["pokemon"] if current_opponent_pokemon else None
                    trainer_pokemon = smart_pokemon_selection(
                        trainer_pokemons, 
                        opponent_current,
                        defeated_trainer_pokemons,
                        current_trainer_pokemon
                    )
                else:
                    available_pokemons = [
                        p for p in trainer_pokemons 
                        if p.pokemon.id not in defeated_trainer_pokemons and 
                        (current_trainer_pokemon is None or p.pokemon.id != current_trainer_pokemon["pokemon"].id)
                    ]
                    if not available_pokemons:
                        raise HTTPException(
                            status_code=400,
                            detail=f"{trainer.name} no tiene Pokémon disponibles para pelear"
                        )
                    trainer_pokemon = random.choice(available_pokemons).pokemon
                
                master_battle_log.append(f"⚡ {trainer.name} elige a {trainer_pokemon.name} (Nv. {trainer_pokemon.level}) para la Batalla {battle_num}!")
                current_trainer_pokemon = None

            # Para el oponente
            if current_opponent_pokemon and current_opponent_pokemon.get("hp_remaining", 0) > 0:
                opponent_pokemon = current_opponent_pokemon["pokemon"]
                master_battle_log.append(f"⚡ {opponent.name} mantiene a {opponent_pokemon.name} en combate! (HP: {current_opponent_pokemon['hp_remaining']}/{opponent_pokemon.hp})")
            else:
                if smart_selection:
                    trainer_current = current_trainer_pokemon["pokemon"] if current_trainer_pokemon else None
                    opponent_pokemon = smart_pokemon_selection(
                        opponent_pokemons, 
                        trainer_current,
                        defeated_opponent_pokemons,
                        current_opponent_pokemon
                    )
                else:
                    available_pokemons = [
                        p for p in opponent_pokemons 
                        if p.pokemon.id not in defeated_opponent_pokemons and 
                        (current_opponent_pokemon is None or p.pokemon.id != current_opponent_pokemon["pokemon"].id)
                    ]
                    if not available_pokemons:
                        raise HTTPException(
                            status_code=400,
                            detail=f"{opponent.name} no tiene Pokémon disponibles para pelear"
                        )
                    opponent_pokemon = random.choice(available_pokemons).pokemon
                
                master_battle_log.append(f"⚡ {opponent.name} saca a {opponent_pokemon.name} (Nv. {opponent_pokemon.level}) al ruedo!")
                current_opponent_pokemon = None
        else:
            # Selección aleatoria simple (sin mantener Pokémon ganadores)
            available_trainer = [p for p in trainer_pokemons if p.pokemon.id not in defeated_trainer_pokemons]
            available_opponent = [p for p in opponent_pokemons if p.pokemon.id not in defeated_opponent_pokemons]
            
            if not available_trainer or not available_opponent:
                raise HTTPException(
                    status_code=400,
                    detail="No hay suficientes Pokémon disponibles para continuar la batalla"
                )
                
            trainer_pokemon = random.choice(available_trainer).pokemon
            opponent_pokemon = random.choice(available_opponent).pokemon
            master_battle_log.append(f"⚡ {trainer.name} elige a {trainer_pokemon.name} (Nv. {trainer_pokemon.level})")
            master_battle_log.append(f"⚡ {opponent.name} elige a {opponent_pokemon.name} (Nv. {opponent_pokemon.level})")

        # Simular la batalla individual
        previous_trainer_hp = current_trainer_pokemon["hp_remaining"] if current_trainer_pokemon else None
        result = await simulate_single_battle(
            db, trainer, opponent, trainer_pokemon, opponent_pokemon, previous_trainer_hp
        )

        # Actualizar niveles de los Pokémon
        if result["trainer_levels_gained"] > 0:
            updated_pokemon = schemas.PokemonUpdate(
                level=trainer_pokemon.level + result["trainer_levels_gained"]
            )
            await crud.update_pokemon(db, trainer_pokemon.id, updated_pokemon)
            trainer_pokemon.level += result["trainer_levels_gained"]

        if result["opponent_levels_gained"] > 0:
            updated_pokemon = schemas.PokemonUpdate(
                level=opponent_pokemon.level + result["opponent_levels_gained"]
            )
            await crud.update_pokemon(db, opponent_pokemon.id, updated_pokemon)
            opponent_pokemon.level += result["opponent_levels_gained"]

        # Actualizar conteo de victorias
        if result["winner"] == "trainer":
            trainer_wins += 1
            defeated_opponent_pokemons.add(result["loser_pokemon"].id)
            if keep_winner_pokemon:
                current_trainer_pokemon = {
                    "pokemon": result["winner_pokemon"],
                    "hp_remaining": result["trainer_hp_remaining"]
                }
                current_opponent_pokemon = None
        elif result["winner"] == "opponent":
            opponent_wins += 1
            defeated_trainer_pokemons.add(result["loser_pokemon"].id)
            if keep_winner_pokemon:
                current_opponent_pokemon = {
                    "pokemon": result["winner_pokemon"],
                    "hp_remaining": result["opponent_hp_remaining"]
                }
                current_trainer_pokemon = None
        else:
            current_trainer_pokemon = None
            current_opponent_pokemon = None

        # Agregar logs al registro maestro
        master_battle_log.extend(result["battle_log"])
        master_battle_log.append(f"🏆 Resultado de la Batalla {battle_num}: ¡{result['winner_name']} se lleva la victoria!")
        master_battle_log.append(f"📊 Marcador: {trainer.name} {trainer_wins} - {opponent_wins} {opponent.name}")

        # Guardar resultados
        battle_results.append(result)

        # Verificar si ya hay un ganador definitivo
        if trainer_wins >= 2 or opponent_wins >= 2:
            break

    # Determinar el ganador general
    if trainer_wins > opponent_wins:
        overall_winner = trainer.name
        overall_winner_id = trainer.id
        overall_loser = opponent.name
        is_trainer_winner = True
        commentator += f" ¡Y con una actuación estelar, {overall_winner} se corona como el campeón de este encuentro! 🎉"
    elif opponent_wins > trainer_wins:
        overall_winner = opponent.name
        overall_winner_id = opponent.id
        overall_loser = trainer.name
        is_trainer_winner = False
        commentator += f" ¡Increíble! ¡{overall_winner} demuestra su poder y se lleva la victoria general! 🏆"
    else:
        overall_winner = "Empate"
        overall_winner_id = None
        overall_loser = "Empate"
        is_trainer_winner = None
        commentator += " ¡Un final reñido! ¡La batalla termina en un empate! 🤝"

    # Determinar Pokémon MVP (mayor daño total o más victorias)
    mvp_data = []
    for result in battle_results:
        # Daño infligido por el Pokémon del entrenador
        trainer_damage = (result["opponent_pokemon"].hp or 100) - result["opponent_hp_remaining"]
        mvp_data.append({
            "pokemon": result["trainer_pokemon"],
            "damage": trainer_damage,
            "wins": 1 if result["winner"] == "trainer" else 0,
            "trainer": trainer.name
        })
        
        # Daño infligido por el Pokémon del oponente
        opponent_damage = (result["trainer_pokemon"].hp or 100) - result["trainer_hp_remaining"]
        mvp_data.append({
            "pokemon": result["opponent_pokemon"],
            "damage": opponent_damage,
            "wins": 1 if result["winner"] == "opponent" else 0,
            "trainer": opponent.name
        })
    
    # Consolidar datos por Pokémon
    mvp_stats = {}
    for data in mvp_data:
        key = data["pokemon"].id
        if key not in mvp_stats:
            mvp_stats[key] = {
                "pokemon": data["pokemon"],
                "total_damage": 0,
                "total_wins": 0,
                "trainer": data["trainer"]
            }
        mvp_stats[key]["total_damage"] += data["damage"]
        mvp_stats[key]["total_wins"] += data["wins"]
    
    # Determinar MVP
    if mvp_stats:
        mvp = max(mvp_stats.values(), key=lambda x: (x["total_wins"], x["total_damage"]))
        mvp_message = (
            f"🏅 MVP del combate: {mvp['pokemon'].name} (Nv. {mvp['pokemon'].level}) de {mvp['trainer']}!"
            f"• Victorias: {mvp['total_wins']}"
            f"• Daño total infligido: {mvp['total_damage']} HP"
            f"• Movimiento más usado: {random.choice(mvp['pokemon'].moves) if hasattr(mvp['pokemon'], 'moves') and mvp['pokemon'].moves else 'Placaje'}"
        )
        master_battle_log.append(mvp_message)

    master_battle_log.append("🎯 RESULTADO FINAL 🎯")
    master_battle_log.append(
        f"{trainer.name}: {trainer_wins} victoria(s) | "
        f"{opponent.name}: {opponent_wins} victoria(s)"
    )
    master_battle_log.append(f"🏅 ¡{overall_winner} gana el combate!")
    master_battle_log.append(f"💬 Comentario del experto: {commentator}")

    # Registro en base de datos
    battle_data = schemas.BattleCreate(
        trainer_id=trainer_id,
        opponent_id=opponent_id,
        is_best_of_three=True
    )

    db_battle = await crud.create_battle(db, battle_data)

    # Actualización con resultado
    if overall_winner != "Empate":
        await crud.update_battle(
            db,
            db_battle.id,
            schemas.BattleUpdate(
                winner=overall_winner,
                date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                battle_log="".join(master_battle_log)
            )
        )

    # Registro de Pokémon participantes (todos los que participaron)
    for result in battle_results:
        await crud.add_pokemon_to_battle(
            db,
            schemas.BattlePokemonCreate(
                battle_id=db_battle.id,
                pokemon_id=result["trainer_pokemon"].id,
                hp_remaining=result["trainer_hp_remaining"],
                participated=True,
                battle_round=battle_results.index(result) + 1
            )
        )
        await crud.add_pokemon_to_battle(
            db,
            schemas.BattlePokemonCreate(
                battle_id=db_battle.id,
                pokemon_id=result["opponent_pokemon"].id,
                hp_remaining=result["opponent_hp_remaining"],
                participated=True,
                battle_round=battle_results.index(result) + 1
            )
        )

    # Obtener la última batalla para los datos finales
    last_battle = battle_results[-1]

    # Resultado detallado
    return schemas.BattleResult(
        battle_id=db_battle.id,
        winner_id=overall_winner_id,
        winner_name=overall_winner,
        loser_name=overall_loser,
        trainer_pokemon=last_battle["trainer_pokemon"],
        opponent_pokemon=last_battle["opponent_pokemon"],
        trainer_hp_remaining=last_battle["trainer_hp_remaining"],
        opponent_hp_remaining=last_battle["opponent_hp_remaining"],
        battle_log=master_battle_log,
        last_trainer_attack=last_battle["last_trainer_attack"],
        last_opponent_attack=last_battle["last_opponent_attack"],
        trainer_wins=trainer_wins,
        opponent_wins=opponent_wins,
        is_best_of_three=True,
        keep_winner_pokemon=keep_winner_pokemon,
        mvp_pokemon=mvp["pokemon"] if mvp_stats else None
    )

# --------------------------------------------------
# ENDPOINTS DE LA API
# --------------------------------------------------

@router.post("/", response_model=schemas.BattleResult)
async def create_battle(
    battle: schemas.BattleCreate,
    db: AsyncSession = Depends(get_db),
    keep_winner_pokemon: bool = True,
    smart_selection: bool = True
):
    """Inicia una nueva batalla entre dos entrenadores (mejor de 3)
    - keep_winner_pokemon: Si True, los Pokémon ganadores permanecen en batalla
    - smart_selection: Si True, los entrenadores eligen Pokémon estratégicamente
    """
    if battle.trainer_id == battle.opponent_id:
        raise HTTPException(
            status_code=400,
            detail="No puedes pelear contra ti mismo"
        )
    return await simulate_battle(db, battle.trainer_id, battle.opponent_id, keep_winner_pokemon, smart_selection)

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