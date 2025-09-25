using Application.Interfaces;
using Core.Entities;
using System.Threading.Tasks;

namespace Application.Services
{
    /// <summary>
    /// Implementa la lógica de negocio para la gestión de Batallas.
    /// </summary>
    public class BattleService : IBattleService
    {
        private readonly IRepository<Battle> _battleRepository;

        public BattleService(IRepository<Battle> battleRepository)
        {
            _battleRepository = battleRepository;
        }

        public async Task<Battle> CreateBattleAsync(Battle battle)
        {
            return await _battleRepository.AddAsync(battle);
        }

        public async Task<Battle?> GetBattleByIdAsync(int id)
        {
            return await _battleRepository.GetByIdAsync(id);
        }
    }
}