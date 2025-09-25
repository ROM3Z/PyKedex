namespace Application.Dtos
{
    /// <summary>
    /// DTO para iniciar una nueva batalla.
    /// </summary>
    public class StartBattleDto
    {
        /// <summary>
        /// ID del primer entrenador (el retador).
        /// </summary>
        public int Trainer1Id { get; set; }

        /// <summary>
        /// ID del segundo entrenador (el oponente).
        /// </summary>
        public int Trainer2Id { get; set; }
    }
}