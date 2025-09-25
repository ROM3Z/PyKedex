namespace Application.Dtos
{
    /// <summary>
    /// DTO para crear un nuevo Entrenador.
    /// </summary>
    public class CreateTrainerDto
    {
        public required string Name { get; set; }
        public required string Email { get; set; }
    }
}