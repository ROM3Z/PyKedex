using Core.Entities;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Application.Interfaces
{
    /// <summary>
    /// Define el contrato para el servicio de gestión de Entrenadores.
    /// </summary>
    public interface ITrainerService
    {
        /// <summary>
        /// Obtiene todos los entrenadores.
        /// </summary>
        /// <returns>Una lista de todos los entrenadores.</returns>
        Task<IEnumerable<Trainer>> GetAllTrainersAsync();

        /// <summary>
        /// Obtiene un entrenador por su ID.
        /// </summary>
        /// <param name="id">El ID del entrenador.</param>
        /// <returns>El entrenador encontrado, o null si no existe.</returns>
        Task<Trainer?> GetTrainerByIdAsync(int id);

        /// <summary>
        /// Crea un nuevo entrenador.
        /// </summary>
        /// <param name="trainer">El entrenador a crear.</param>
        /// <returns>El entrenador creado.</returns>
        Task<Trainer> CreateTrainerAsync(Trainer trainer);

        /// <summary>
        /// Agrega un Pokémon a la colección de un entrenador.
        /// </summary>
        /// <param name="trainerId">El ID del entrenador.</param>
        /// <param name="pokemonId">El ID del Pokémon a agregar.</param>
        /// <param name="isShiny">Indica si el Pokémon es shiny.</param>
        Task AddPokemonToTrainerAsync(int trainerId, int pokemonId, bool isShiny);
    }
}