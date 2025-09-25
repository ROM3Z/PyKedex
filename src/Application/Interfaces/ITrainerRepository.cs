using Core.Entities;
using System.Threading.Tasks;

namespace Application.Interfaces
{
    /// <summary>
    /// Repositorio específico para la entidad Trainer, extendiendo el genérico.
    /// </summary>
    public interface ITrainerRepository : IRepository<Trainer>
    {
        /// <summary>
        /// Obtiene un entrenador por su ID, incluyendo su lista de Pokémon.
        /// </summary>
        /// <param name="id">El ID del entrenador.</param>
        /// <returns>El entrenador con su equipo de Pokémon, o null si no se encuentra.</returns>
        Task<Trainer?> GetByIdWithPokemonsAsync(int id);
    }
}