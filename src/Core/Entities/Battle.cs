using System;
using System.Collections.Generic;

namespace Core.Entities
{
    /// <summary>
    /// Representa una batalla Pokémon entre un entrenador y un oponente.
    /// </summary>
    public class Battle
    {
        /// <summary>
        /// ID único de la batalla.
        /// </summary>
        public int Id { get; set; }

        /// <summary>
        /// ID del entrenador que participa en la batalla.
        /// </summary>
        public int TrainerId { get; set; }

        /// <summary>
        /// Nombre del oponente en la batalla.
        /// </summary>
        public required string OpponentName { get; set; }

        /// <summary>
        /// Nombre del ganador de la batalla. Puede ser nulo en caso de empate.
        /// </summary>
        public string? Winner { get; set; }

        /// <summary>
        /// Fecha y hora en que se realizó la batalla.
        /// </summary>
        public DateTime Date { get; set; } = DateTime.UtcNow;

        // Propiedades de navegación

        /// <summary>
        /// Referencia al entrenador que participó en la batalla.
        /// </summary>
        public Trainer Trainer { get; set; } = null!;

        /// <summary>
        /// Pokémon que participaron en esta batalla.
        /// </summary>
        public ICollection<BattlePokemon> Pokemons { get; set; } = new List<BattlePokemon>();

        /// <summary>
        /// Registros de eventos que ocurrieron durante la batalla.
        /// </summary>
        public ICollection<BattleLog> Logs { get; set; } = new List<BattleLog>();
    }
}