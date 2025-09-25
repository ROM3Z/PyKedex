namespace Core.Entities
{
    /// <summary>
    /// Modelo de relación que asocia un Entrenador con un Pokémon.
    /// Representa una instancia de un Pokémon que pertenece a un entrenador.
    /// </summary>
    public class TrainerPokemon
    {
        /// <summary>
        /// ID del entrenador.
        /// </summary>
        public int TrainerId { get; set; }

        /// <summary>
        /// ID del Pokémon.
        /// </summary>
        public int PokemonId { get; set; }

        /// <summary>
        /// Indica si esta instancia específica del Pokémon es una variante "shiny".
        /// </summary>
        public bool IsShiny { get; set; } = false;

        // Propiedades de navegación para acceder a las entidades relacionadas

        /// <summary>
        /// Referencia al Entrenador.
        /// </summary>
        public Trainer Trainer { get; set; } = null!;

        /// <summary>
        /// Referencia al Pokémon.
        /// </summary>
        public Pokemon Pokemon { get; set; } = null!;
    }
}