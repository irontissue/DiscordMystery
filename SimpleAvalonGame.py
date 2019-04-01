from discord.ext import commands
import Role
import logging
import Phase
from Game import Game

logging.basicConfig(level=logging.INFO)


class SimpleAvalonGame(Game):

    minimum_players = 1

    ALL_ROLES = {'merlin': lambda: Role.Merlin(),
                 'mordred': lambda: Role.Mordred(),
                 'oberon': lambda: Role.Oberon(),
                 'morgana': lambda: Role.Morgana(),
                 'percival': lambda: Role.Percival(),
                 'loyal Servant': lambda: Role.LoyalServant(),
                 'minion of Mordred': lambda: Role.MinionOfMordred(),
                 'good': lambda: Role.LoyalServant(),
                 'bad': lambda: Role.MinionOfMordred()}

    def __init__(self, ctx, bot, wanted_roles=None):
        super().__init__(ctx, bot, wanted_roles)
        if wanted_roles is None:
            self.wanted_roles = []
        else:
            self.wanted_roles = wanted_roles
        self.roles = []
        self.add_phase(Phase.TestDiscuss(self))

    async def game_init(self):
        try:
            if len(self.players) >= self.minimum_players:
                await self.ctx.send("Game initialized with players: ")
                await self.ctx.send(', '.join(str(p.name) for p in self.players))
                await self.ctx.send("Game initialized with channels: ")
                await self.ctx.send(', '.join(str(p.name) for p in self.channels))
            else:
                await self.ctx.send("Game cannot start without a minimum of " + str(self.minimum_players) + " players!")
                return False
            valid, response = Role.Role.check_valid_roles(self.wanted_roles, self.ALL_ROLES)
            if valid:
                await self.ctx.send("Game initialized with roles: ")
                if len(response) != 0:
                    await self.ctx.send(", ".join(str(p.name) for p in response))
                else:
                    await self.ctx.send("No special roles.")
                self.roles = response
                return True
            else:
                await self.ctx.send(response)
                return False
        except:
            return False

    async def start_game(self):
        await super().start_game()
