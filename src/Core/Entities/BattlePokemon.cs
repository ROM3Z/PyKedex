namespace Core.Entities
{
    /// <summary>
    /// Modelo de relación que asocia una Batalla con un Pokémon participante.
    /// </summary>
    public class BattlePokemon
    {
        /// <summary>
        /// ID único de esta entrada de participación.
        /// </summary>
        public int Id { get; set; }

        /// <summary>
        /// ID de la batalla.
        /// </summary>
        public int BattleId { get; set; }

        /// <summary>
        /// ID del Pokémon.
        /// </summary>
        public int PokemonId { get; set; }

        /// <summary>
        /// HP restante del Pokémon al finalizar la batalla.
        /// </summary>
        public int HpRemaining { get; set; }

        /// <summary>
        /// Indica si el Pokémon participó activamente en el combate.
        /// </summary>
        public bool Participated { get; set; } = false;

        // Propiedades de navegación

        /// <summary>
        /// Referencia a la Batalla.
        /// </summary>
        public Battle Battle { get; set; } = null!;

        /// <summary>
        /// Referencia al Pokémon.
        /// </summary>
        public Pokemon Pokemon { get; set; } = null!;
    }
}