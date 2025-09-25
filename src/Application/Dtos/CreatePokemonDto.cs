using System.Collections.Generic;

namespace Application.Dtos
{
    /// <summary>
    /// DTO para crear un nuevo Pokémon.
    /// </summary>
    public class CreatePokemonDto
    {
        public required string Name { get; set; }
        public string? Element { get; set; }
        public int Hp { get; set; }
        public int Attack { get; set; }
        public int Defense { get; set; }
        public int SpecialAttack { get; set; }
        public int SpecialDefense { get; set; }
        public int Speed { get; set; }
        public List<string> Moves { get; set; } = new List<string>();
        public int Level { get; set; } = 1;
    }
}