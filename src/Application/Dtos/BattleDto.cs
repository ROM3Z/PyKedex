using System;

namespace Application.Dtos
{
    /// <summary>
    /// DTO para transferir datos de una Batalla.
    /// </summary>
    public class BattleDto
    {
        public int Id { get; set; }
        public int TrainerId { get; set; }
        public required string OpponentName { get; set; }
        public string? Winner { get; set; }
        public DateTime Date { get; set; }
    }
}