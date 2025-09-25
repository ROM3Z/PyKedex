using System.Collections.Generic;
using System.Threading.Tasks;

namespace Application.Interfaces
{
    /// <summary>
    /// Define un contrato genérico para las operaciones de repositorio.
    /// Esto nos permite abstraer el acceso a datos para cualquier entidad.
    /// </summary>
    /// <typeparam name="T">La entidad con la que trabajará el repositorio.</typeparam>
    public interface IRepository<T> where T : class
    {
        /// <summary>
        /// Obtiene una entidad por su ID.
        /// </summary>
        /// <param name="id">El ID de la entidad.</param>
        /// <returns>La entidad encontrada, o null si no existe.</returns>
        Task<T?> GetByIdAsync(int id);

        /// <summary>
        /// Obtiene todas las entidades de un tipo.
        /// </summary>
        /// <returns>Una lista de todas las entidades.</returns>
        Task<IReadOnlyList<T>> ListAllAsync();

        /// <summary>
        /// Agrega una nueva entidad a la base de datos.
        /// </summary>
        /// <param name="entity">La entidad a agregar.</param>
        /// <returns>La entidad agregada.</returns>
        Task<T> AddAsync(T entity);

        /// <summary>
        /// Actualiza una entidad existente.
        /// </summary>
        /// <param name="entity">La entidad a actualizar.</param>
        Task UpdateAsync(T entity);

        /// <summary>
        /// Elimina una entidad de la base de datos.
        /// </summary>
        /// <param name="entity">La entidad a eliminar.</param>
        Task DeleteAsync(T entity);
    }
}