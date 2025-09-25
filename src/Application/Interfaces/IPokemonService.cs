using Core.Entities;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Application.Interfaces
{
    /// <summary>
    /// Define el contrato para el servicio de gestión de Pokémon.
    /// </summary>
    public interface IPokemonService
    {
        /// <summary>
        /// Obtiene todos los Pokémon.
        /// </summary>
        /// <returns>Una lista de todos los Pokémon.</returns>
        Task<IEnumerable<Pokemon>> GetAllPokemonsAsync();

        /// <summary>
        /// Obtiene un Pokémon por su ID.
        /// </summary>
        /// <param name="id">El ID del Pokémon.</param>
        /// <returns>El Pokémon encontrado, o null si no existe.</returns>
        Task<Pokemon?> GetPokemonByIdAsync(int id);

        /// <summary>
        /// Crea un nuevo Pokémon.
        /// </summary>
        /// <param name="pokemon">El Pokémon a crear.</param>
        /// <returns>El Pokémon creado.</returns>
        Task<Pokemon> CreatePokemonAsync(Pokemon pokemon);

        /// <summary>
        /// Actualiza un Pokémon existente.
        /// </summary>
        /// <param name="pokemon">El Pokémon a actualizar.</param>
        Task UpdatePokemonAsync(Pokemon pokemon);

        /// <summary>
        /// Elimina un Pokémon por su ID.
        /// </summary>
        /// <param name="id">El ID del Pokémon a eliminar.</param>
        Task DeletePokemonAsync(int id);
    }
}