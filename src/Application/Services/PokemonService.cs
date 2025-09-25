using Application.Interfaces;
using Core.Entities;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Application.Services
{
    /// <summary>
    /// Implementa la lógica de negocio para la gestión de Pokémon.
    /// </summary>
    public class PokemonService : IPokemonService
    {
        private readonly IRepository<Pokemon> _pokemonRepository;

        /// <summary>
        /// Inicializa una nueva instancia del servicio de Pokémon.
        /// </summary>
        /// <param name="pokemonRepository">El repositorio para las operaciones de datos de Pokémon.</param>
        public PokemonService(IRepository<Pokemon> pokemonRepository)
        {
            _pokemonRepository = pokemonRepository;
        }

        public async Task<IEnumerable<Pokemon>> GetAllPokemonsAsync()
        {
            return await _pokemonRepository.ListAllAsync();
        }

        public async Task<Pokemon?> GetPokemonByIdAsync(int id)
        {
            return await _pokemonRepository.GetByIdAsync(id);
        }

        public async Task<Pokemon> CreatePokemonAsync(Pokemon pokemon)
        {
            return await _pokemonRepository.AddAsync(pokemon);
        }

        public async Task UpdatePokemonAsync(Pokemon pokemon)
        {
            await _pokemonRepository.UpdateAsync(pokemon);
        }

        public async Task DeletePokemonAsync(int id)
        {
            var pokemon = await _pokemonRepository.GetByIdAsync(id);
            if (pokemon != null)
            {
                await _pokemonRepository.DeleteAsync(pokemon);
            }
        }
    }
}