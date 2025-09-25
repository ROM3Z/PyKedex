namespace Core.Entities
{
    /// <summary>
    /// Representa un Entrenador Pokémon en el sistema.
    /// Contiene la información básica y las relaciones del entrenador.
    /// </summary>
    public class Trainer
    {
        /// <summary>
        /// ID único del entrenador.
        /// </summary>
        public int Id { get; set; }

        /// <summary>
        /// Nombre del entrenador. Es un campo obligatorio.
        /// </summary>
        public required string Name { get; set; }

        /// <summary>
        /// Correo electrónico del entrenador. Debe ser único.
        /// </summary>
        public required string Email { get; set; }

        /// <summary>
        /// Nivel del entrenador, que puede aumentar con la experiencia.
        /// </summary>
        public int Level { get; set; } = 1;

        // Propiedades de navegación para las relaciones

        /// <summary>
        /// Colección de los Pokémon que pertenecen a este entrenador.
        /// Esta es la tabla de unión entre Trainer y Pokemon.
        /// </summary>
        public ICollection<TrainerPokemon> Pokemons { get; set; } = new List<TrainerPokemon>();

        /// <summary>
        /// Historial de batallas en las que ha participado el entrenador.
        /// </summary>
        public ICollection<Battle> Battles { get; set; } = new List<Battle>();
    }
}