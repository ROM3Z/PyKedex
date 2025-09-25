namespace Application.Dtos
{
    /// <summary>
    /// DTO para transferir datos de un Entrenador.
    /// </summary>
    public class TrainerDto
    {
        public int Id { get; set; }
        public required string Name { get; set; }
        public required string Email { get; set; }
        public int Level { get; set; }
        public List<PokemonDto> Pokemons { get; set; } = new List<PokemonDto>();
    }
}