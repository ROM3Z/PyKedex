using Application.Dtos;
using Application.Interfaces;
using Core.Entities;
using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class PokemonsController : ControllerBase
    {
        private readonly IPokemonService _pokemonService;

        public PokemonsController(IPokemonService pokemonService)
        {
            _pokemonService = pokemonService;
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<PokemonDto>>> GetPokemons()
        {
            var pokemons = await _pokemonService.GetAllPokemonsAsync();
            var pokemonDtos = pokemons.Select(p => new PokemonDto
            {
                Id = p.Id,
                Name = p.Name,
                Element = p.Element,
                Hp = p.Hp,
                Attack = p.Attack,
                Defense = p.Defense,
                SpecialAttack = p.SpecialAttack,
                SpecialDefense = p.SpecialDefense,
                Speed = p.Speed,
                Moves = p.Moves,
                Level = p.Level
            });
            return Ok(pokemonDtos);
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<PokemonDto>> GetPokemon(int id)
        {
            var pokemon = await _pokemonService.GetPokemonByIdAsync(id);
            if (pokemon == null)
            {
                return NotFound();
            }
            var pokemonDto = new PokemonDto
            {
                Id = pokemon.Id,
                Name = pokemon.Name,
                Element = pokemon.Element,
                Hp = pokemon.Hp,
                Attack = pokemon.Attack,
                Defense = pokemon.Defense,
                SpecialAttack = pokemon.SpecialAttack,
                SpecialDefense = pokemon.SpecialDefense,
                Speed = pokemon.Speed,
                Moves = pokemon.Moves,
                Level = pokemon.Level
            };
            return Ok(pokemonDto);
        }

        [HttpPost]
        public async Task<ActionResult<PokemonDto>> CreatePokemon(CreatePokemonDto createPokemonDto)
        {
            var pokemon = new Pokemon
            {
                Name = createPokemonDto.Name,
                Element = createPokemonDto.Element,
                Hp = createPokemonDto.Hp,
                Attack = createPokemonDto.Attack,
                Defense = createPokemonDto.Defense,
                SpecialAttack = createPokemonDto.SpecialAttack,
                SpecialDefense = createPokemonDto.SpecialDefense,
                Speed = createPokemonDto.Speed,
                Moves = createPokemonDto.Moves,
                Level = createPokemonDto.Level
            };

            var createdPokemon = await _pokemonService.CreatePokemonAsync(pokemon);

            var pokemonDto = new PokemonDto
            {
                Id = createdPokemon.Id,
                Name = createdPokemon.Name,
                Element = createdPokemon.Element,
                Hp = createdPokemon.Hp,
                Attack = createdPokemon.Attack,
                Defense = createdPokemon.Defense,
                SpecialAttack = createdPokemon.SpecialAttack,
                SpecialDefense = createdPokemon.SpecialDefense,
                Speed = createdPokemon.Speed,
                Moves = createdPokemon.Moves,
                Level = createdPokemon.Level
            };

            return CreatedAtAction(nameof(GetPokemon), new { id = createdPokemon.Id }, pokemonDto);
        }
    }
}