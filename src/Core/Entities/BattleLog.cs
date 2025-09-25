namespace Core.Entities
{
    /// <summary>
    /// Registra un evento que ocurrió durante una batalla.
    /// </summary>
    public class BattleLog
    {
        /// <summary>
        /// ID único del log.
        /// </summary>
        public int Id { get; set; }

        /// <summary>
        /// ID de la batalla a la que pertenece este log.
        /// </summary>
        public int BattleId { get; set; }

        /// <summary>
        /// El número de turno en el que ocurrió el evento.
        /// </summary>
        public int TurnNumber { get; set; }

        /// <summary>
        /// Descripción de la acción que tuvo lugar (ej: "Pikachu usó Placaje").
        /// </summary>
        public required string Action { get; set; }

        // Propiedad de navegación

        /// <summary>
        /// Referencia a la Batalla.
        /// </summary>
        public Battle Battle { get; set; } = null!;
    }
}