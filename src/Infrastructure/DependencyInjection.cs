using Application.Interfaces;
using Infrastructure.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace Infrastructure
{
    /// <summary>
    /// Clase para registrar las dependencias de la capa de infraestructura.
    /// </summary>
    public static class DependencyInjection
    {
        public static IServiceCollection AddInfrastructure(this IServiceCollection services, IConfiguration configuration)
        {
            // Configura el DbContext para usar SQLite.
            // La cadena de conexión se obtiene del archivo de configuración (appsettings.json).
            services.AddDbContext<AppDbContext>(options =>
                options.UseSqlite(configuration.GetConnectionString("DefaultConnection")));

            // Registra el repositorio genérico.
            // Esto permite que cualquier servicio pueda inyectar IRepository<T>.
            services.AddScoped(typeof(IRepository<>), typeof(EfRepository<>));

            // Registra repositorios específicos.
            services.AddScoped<ITrainerRepository, TrainerRepository>();

            return services;
        }
    }
}