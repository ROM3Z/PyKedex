using Core.Entities;
using Microsoft.EntityFrameworkCore;

namespace Infrastructure.Data
{
    /// <summary>
    /// Contexto de la base de datos para la aplicación.
    /// Representa la sesión con la base de datos y permite consultar y guardar entidades.
    /// </summary>
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
        {
        }

        // Define los DbSet para cada entidad que EF Core debe gestionar.
        public DbSet<Pokemon> Pokemons { get; set; }
        public DbSet<Trainer> Trainers { get; set; }
        public DbSet<TrainerPokemon> TrainerPokemons { get; set; }
        public DbSet<Battle> Battles { get; set; }
        public DbSet<BattlePokemon> BattlePokemons { get; set; }
        public DbSet<Admin> Admins { get; set; }

        /// <summary>
        /// Configura el modelo de la base de datos, incluyendo claves primarias,
        /// claves foráneas y relaciones.
        /// </summary>
        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // Configuración para la entidad TrainerPokemon (relación muchos a muchos)
            modelBuilder.Entity<TrainerPokemon>()
                .HasKey(tp => new { tp.TrainerId, tp.PokemonId }); // Clave primaria compuesta

            modelBuilder.Entity<TrainerPokemon>()
                .HasOne(tp => tp.Trainer)
                .WithMany(t => t.Pokemons)
                .HasForeignKey(tp => tp.TrainerId);

            modelBuilder.Entity<TrainerPokemon>()
                .HasOne(tp => tp.Pokemon)
                .WithMany() // Un Pokémon puede estar en muchas colecciones de entrenadores
                .HasForeignKey(tp => tp.PokemonId);

            // Configuración para la entidad Battle
            modelBuilder.Entity<Battle>()
                .HasOne(b => b.Trainer)
                .WithMany(t => t.Battles)
                .HasForeignKey(b => b.TrainerId);
        }
    }
}