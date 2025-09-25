using Application.Dtos;
using Application.Interfaces;
using Core.Entities;
using System;
using System.Linq;
using System.Threading.Tasks;

namespace Application.Services
{
    /// <summary>
    /// Implementa la lógica de negocio para la gestión de Batallas.
    /// </summary>
    public class BattleService : IBattleService
    {
        private readonly IRepository<Battle> _battleRepository;
        private readonly ITrainerRepository _trainerRepository;

        public BattleService(IRepository<Battle> battleRepository, ITrainerRepository trainerRepository)
        {
            _battleRepository = battleRepository;
            _trainerRepository = trainerRepository;
        }

        public async Task<BattleResultDto> SimulateBattleAsync(int trainer1Id, int trainer2Id)
        {
            var trainer1 = await _trainerRepository.GetByIdWithPokemonsAsync(trainer1Id);
            var trainer2 = await _trainerRepository.GetByIdWithPokemonsAsync(trainer2Id);

            if (trainer1 == null || trainer2 == null)
                throw new Exception("Uno o ambos entrenadores no fueron encontrados.");
            if (!trainer1.Pokemons.Any() || !trainer2.Pokemons.Any())
                throw new Exception("Uno o ambos entrenadores no tienen Pokémon para luchar.");

            var battle = new Battle
            {
                TrainerId = trainer1.Id,
                OpponentName = trainer2.Name,
                Date = DateTime.UtcNow
            };

            var team1 = trainer1.Pokemons.Select(p => p.Pokemon).ToList();
            var team2 = trainer2.Pokemons.Select(p => p.Pokemon).ToList();
            team1.ForEach(p => p.CurrentHp = p.Hp);
            team2.ForEach(p => p.CurrentHp = p.Hp);

            int turn = 1;
            var logs = new List<BattleLog>();

            while (team1.Any(p => p.CurrentHp > 0) && team2.Any(p => p.CurrentHp > 0))
            {
                var activePokemon1 = team1.First(p => p.CurrentHp > 0);
                var activePokemon2 = team2.First(p => p.CurrentHp > 0);

                Pokemon attacker, defender;
                if (activePokemon1.Speed >= activePokemon2.Speed)
                {
                    attacker = activePokemon1;
                    defender = activePokemon2;
                }
                else
                {
                    attacker = activePokemon2;
                    defender = activePokemon1;
                }

                // Primer ataque
                int damage = Math.Max(1, (attacker.Attack * 10) / defender.Defense);
                defender.CurrentHp = Math.Max(0, defender.CurrentHp - damage);
                logs.Add(new BattleLog { TurnNumber = turn, Action = $"{attacker.Name} ataca a {defender.Name} e inflige {damage} de daño. {defender.Name} tiene {defender.CurrentHp} HP restante." });

                if (defender.CurrentHp <= 0)
                {
                    logs.Add(new BattleLog { TurnNumber = turn, Action = $"{defender.Name} ha sido debilitado." });
                    continue; // Pasa al siguiente turno si el defensor es debilitado
                }

                // Segundo ataque (el otro Pokémon)
                attacker = defender; // El defensor ahora es el atacante
                defender = (attacker == activePokemon1) ? activePokemon2 : activePokemon1;

                damage = Math.Max(1, (attacker.Attack * 10) / defender.Defense);
                defender.CurrentHp = Math.Max(0, defender.CurrentHp - damage);
                logs.Add(new BattleLog { TurnNumber = turn, Action = $"{attacker.Name} ataca a {defender.Name} e inflige {damage} de daño. {defender.Name} tiene {defender.CurrentHp} HP restante." });

                if (defender.CurrentHp <= 0)
                {
                    logs.Add(new BattleLog { TurnNumber = turn, Action = $"{defender.Name} ha sido debilitado." });
                }

                turn++;
            }

            Trainer? winner = team1.Any(p => p.CurrentHp > 0) ? trainer1 : trainer2;
            battle.Winner = winner.Name;
            battle.Logs = logs;

            var createdBattle = await _battleRepository.AddAsync(battle);

            return new BattleResultDto
            {
                BattleId = createdBattle.Id,
                Trainer1Id = trainer1.Id,
                Trainer1Name = trainer1.Name,
                Trainer2Id = trainer2.Id,
                Trainer2Name = trainer2.Name,
                WinnerId = winner.Id,
                WinnerName = winner.Name,
                Date = createdBattle.Date,
                Logs = createdBattle.Logs.Select(l => $"Turno {l.TurnNumber}: {l.Action}").ToList()
            };
        }

        public async Task<Battle?> GetBattleByIdAsync(int id)
        {
            return await _battleRepository.GetByIdAsync(id);
        }
    }
}