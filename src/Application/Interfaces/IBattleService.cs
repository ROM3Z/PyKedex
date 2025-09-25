using Application.Dtos;
using Core.Entities;
using System.Threading.Tasks;

namespace Application.Interfaces
{
    /// <summary>
    /// Define el contrato para el servicio de gestión de Batallas.
    /// </summary>
    public interface IBattleService
    {
        /// <summary>
        /// Simula una batalla entre dos entrenadores y guarda el resultado.
        /// </summary>
        /// <param name="trainer1Id">El ID del primer entrenador.</param>
        /// <param name="trainer2Id">El ID del segundo entrenador.</param>
        /// <returns>El resultado de la batalla.</returns>
        Task<BattleResultDto> SimulateBattleAsync(int trainer1Id, int trainer2Id);

        /// <summary>
        /// Obtiene una batalla por su ID.
        /// </summary>
        /// <param name="id">El ID de la batalla.</param>
        /// <returns>La batalla encontrada, o null si no existe.</returns>
        Task<Battle?> GetBattleByIdAsync(int id);
    }
}