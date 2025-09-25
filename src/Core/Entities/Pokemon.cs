namespace Core.Entities
{
    /// <summary>
    /// Representa un Pokémon en el sistema.
    /// Contiene todos los atributos y estadísticas base de un Pokémon.
    /// </summary>
    public class Pokemon
    {
        /// <summary>
        /// ID único del Pokémon en la base de datos.
        /// </summary>
        public int Id { get; set; }

        /// <summary>
        /// Nombre del Pokémon (ej: "Pikachu", "Charizard").
        /// Es un campo obligatorio.
        /// </summary>
        public required string Name { get; set; }

        /// <summary>
        /// Tipo(s) elemental(es) del Pokémon (ej: "Fuego", "Agua/Volador").
        /// </summary>
        public string? Element { get; set; }

        /// <summary>
        /// Puntos de Salud (HP) base del Pokémon.
        /// </summary>
        public int Hp { get; set; }

        /// <summary>
        /// Estadística de Ataque físico base.
        /// </summary>
        public int Attack { get; set; }

        /// <summary>
        /// Estadística de Defensa física base.
        /// </summary>
        public int Defense { get; set; }

        /// <summary>
        /// Estadística de Ataque Especial base.
        /// </summary>
        public int SpecialAttack { get; set; }

        /// <summary>
        /// Estadística de Defensa Especial base.
        /// </summary>
        public int SpecialDefense { get; set; }

        /// <summary>
        /// Estadística de Velocidad base.
        /// </summary>
        public int Speed { get; set; }

        /// <summary>
        /// Lista de movimientos que el Pokémon puede aprender o usar.
        /// </summary>
        public List<string> Moves { get; set; } = new List<string>();

        /// <summary>
        /// Nivel actual del Pokémon.
        /// </summary>
        public int Level { get; set; } = 1;

        /// <summary>
        /// HP actual del Pokémon, usado en combates.
        /// No se mapea a la base de datos ya que es un estado temporal.
        /// </summary>
        [System.ComponentModel.DataAnnotations.Schema.NotMapped]
        public int CurrentHp { get; set; }
    }
}