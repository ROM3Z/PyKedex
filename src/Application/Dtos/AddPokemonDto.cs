namespace Application.Dtos
{
    /// <summary>
    /// DTO para agregar un Pokémon a un entrenador.
    /// </summary>
    public class AddPokemonDto
    {
        public int PokemonId { get; set; }
        public bool IsShiny { get; set; }
    }
}