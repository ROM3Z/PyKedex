using Application.Interfaces;
using Core.Entities;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Application.Services
{
    /// <summary>
    /// Implementa la lógica de negocio para la gestión de Entrenadores.
    /// </summary>
    public class TrainerService : ITrainerService
    {
        private readonly IRepository<Trainer> _trainerRepository;
        private readonly IRepository<Pokemon> _pokemonRepository;
        private readonly IRepository<TrainerPokemon> _trainerPokemonRepository;

        public TrainerService(
            IRepository<Trainer> trainerRepository,
            IRepository<Pokemon> pokemonRepository,
            IRepository<TrainerPokemon> trainerPokemonRepository)
        {
            _trainerRepository = trainerRepository;
            _pokemonRepository = pokemonRepository;
            _trainerPokemonRepository = trainerPokemonRepository;
        }

        public async Task<IEnumerable<Trainer>> GetAllTrainersAsync()
        {
            return await _trainerRepository.ListAllAsync();
        }

        public async Task<Trainer?> GetTrainerByIdAsync(int id)
        {
            return await _trainerRepository.GetByIdAsync(id);
        }

        public async Task<Trainer> CreateTrainerAsync(Trainer trainer)
        {
            return await _trainerRepository.AddAsync(trainer);
        }

        public async Task AddPokemonToTrainerAsync(int trainerId, int pokemonId, bool isShiny)
        {
            var trainer = await _trainerRepository.GetByIdAsync(trainerId);
            var pokemon = await _pokemonRepository.GetByIdAsync(pokemonId);

            if (trainer != null && pokemon != null)
            {
                var trainerPokemon = new TrainerPokemon
                {
                    TrainerId = trainerId,
                    PokemonId = pokemonId,
                    IsShiny = isShiny
                };
                await _trainerPokemonRepository.AddAsync(trainerPokemon);
            }
        }
    }
}