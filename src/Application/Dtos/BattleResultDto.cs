using System;

namespace Application.Dtos
{
    /// <summary>
    /// DTO para devolver el resultado de una batalla.
    /// </summary>
    public class BattleResultDto
    {
        public int BattleId { get; set; }
        public int Trainer1Id { get; set; }
        public string Trainer1Name { get; set; } = string.Empty;
        public int Trainer2Id { get; set; }
        public string Trainer2Name { get; set; } = string.Empty;
        public int? WinnerId { get; set; }
        public string? WinnerName { get; set; }
        public DateTime Date { get; set; }
        public List<string> Logs { get; set; } = new List<string>();
    }
}