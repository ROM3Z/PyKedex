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
    public class TrainersController : ControllerBase
    {
        private readonly ITrainerService _trainerService;

        public TrainersController(ITrainerService trainerService)
        {
            _trainerService = trainerService;
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<TrainerDto>>> GetTrainers()
        {
            var trainers = await _trainerService.GetAllTrainersAsync();
            var trainerDtos = trainers.Select(t => new TrainerDto
            {
                Id = t.Id,
                Name = t.Name,
                Email = t.Email,
                Level = t.Level
            });
            return Ok(trainerDtos);
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<TrainerDto>> GetTrainer(int id)
        {
            var trainer = await _trainerService.GetTrainerByIdAsync(id);
            if (trainer == null)
            {
                return NotFound();
            }
            var trainerDto = new TrainerDto
            {
                Id = trainer.Id,
                Name = trainer.Name,
                Email = trainer.Email,
                Level = trainer.Level
            };
            return Ok(trainerDto);
        }

        [HttpPost]
        public async Task<ActionResult<TrainerDto>> CreateTrainer(CreateTrainerDto createTrainerDto)
        {
            var trainer = new Trainer
            {
                Name = createTrainerDto.Name,
                Email = createTrainerDto.Email
            };

            var createdTrainer = await _trainerService.CreateTrainerAsync(trainer);

            var trainerDto = new TrainerDto
            {
                Id = createdTrainer.Id,
                Name = createdTrainer.Name,
                Email = createdTrainer.Email,
                Level = createdTrainer.Level
            };

            return CreatedAtAction(nameof(GetTrainer), new { id = createdTrainer.Id }, trainerDto);
        }

        [HttpPost("{trainerId}/pokemons")]
        public async Task<IActionResult> AddPokemonToTrainer(int trainerId, [FromBody] AddPokemonDto addPokemonDto)
        {
            await _trainerService.AddPokemonToTrainerAsync(trainerId, addPokemonDto.PokemonId, addPokemonDto.IsShiny);
            return NoContent();
        }
    }
}