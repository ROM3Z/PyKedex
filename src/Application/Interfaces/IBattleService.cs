using Core.Entities;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Application.Interfaces
{
    /// <summary>
    /// Define el contrato para el servicio de gestión de Batallas.
    /// </summary>
    public interface IBattleService
    {
        /// <summary>
        /// Inicia una nueva batalla.
        /// </summary>
        /// <param name="battle">La información de la batalla a crear.</param>
        /// <returns>La batalla creada.</returns>
        Task<Battle> CreateBattleAsync(Battle battle);

        /// <summary>
        /// Obtiene una batalla por su ID.
        /// </summary>
        /// <param name="id">El ID de la batalla.</param>
        /// <returns>La batalla encontrada, o null si no existe.</returns>
        Task<Battle?> GetBattleByIdAsync(int id);
    }
}