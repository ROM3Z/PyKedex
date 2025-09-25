using Application.Dtos;
using Application.Interfaces;
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;

namespace Api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class BattlesController : ControllerBase
    {
        private readonly IBattleService _battleService;

        public BattlesController(IBattleService battleService)
        {
            _battleService = battleService;
        }

        [HttpPost("simulate")]
        public async Task<ActionResult<BattleResultDto>> SimulateBattle([FromBody] StartBattleDto startBattleDto)
        {
            try
            {
                var result = await _battleService.SimulateBattleAsync(startBattleDto.Trainer1Id, startBattleDto.Trainer2Id);
                return Ok(result);
            }
            catch (System.Exception ex)
            {
                // En una aplicación real, registraríamos el error.
                // Aquí, devolvemos un BadRequest con el mensaje de la excepción.
                return BadRequest(ex.Message);
            }
        }
    }
}