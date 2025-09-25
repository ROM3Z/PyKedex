namespace Application.Dtos
{
    /// <summary>
    /// DTO para transferir datos de un Pokémon.
    /// </summary>
    public class PokemonDto
    {
        public int Id { get; set; }
        public required string Name { get; set; }
        public string? Element { get; set; }
        public int Hp { get; set; }
        public int Attack { get; set; }
        public int Defense { get; set; }
        public int SpecialAttack { get; set; }
        public int SpecialDefense { get; set; }
        public int Speed { get; set; }
        public List<string> Moves { get; set; } = new List<string>();
        public int Level { get; set; }
    }
}