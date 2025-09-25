using Application.Interfaces;
using Core.Entities;
using Microsoft.EntityFrameworkCore;
using System.Threading.Tasks;

namespace Infrastructure.Data
{
    /// <summary>
    /// Implementación del repositorio específico para la entidad Trainer.
    /// </summary>
    public class TrainerRepository : EfRepository<Trainer>, ITrainerRepository
    {
        public TrainerRepository(AppDbContext dbContext) : base(dbContext)
        {
        }

        /// <summary>
        /// Obtiene un entrenador por su ID, incluyendo su lista de Pokémon.
        /// </summary>
        public async Task<Trainer?> GetByIdWithPokemonsAsync(int id)
        {
            return await _dbContext.Trainers
                .Include(t => t.Pokemons)
                    .ThenInclude(tp => tp.Pokemon)
                .FirstOrDefaultAsync(t => t.Id == id);
        }
    }
}