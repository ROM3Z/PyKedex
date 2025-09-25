using Application.Interfaces;
using Application.Services;
using Microsoft.Extensions.DependencyInjection;

namespace Application
{
    /// <summary>
    /// Clase para registrar las dependencias de la capa de aplicación.
    /// </summary>
    public static class DependencyInjection
    {
        public static IServiceCollection AddApplication(this IServiceCollection services)
        {
            // Registra los servicios de la aplicación con sus interfaces.
            // Esto permite que la capa de presentación (API) los inyecte.
            services.AddScoped<IPokemonService, PokemonService>();
            services.AddScoped<ITrainerService, TrainerService>();
            services.AddScoped<IBattleService, BattleService>();

            return services;
        }
    }
}