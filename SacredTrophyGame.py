import Role
import logging
import Phase
from Game import Game
import discord

logging.basicConfig(level=logging.INFO)


class SacredTrophyGame(Game):

    minimum_players = 5

    ALL_ROLES = {'good': lambda: Role.LightServant(),
                 'bad': lambda: Role.DarkServant()}

    HELP_DESCRIPTION = "Game help: Figure it out, tough luck lol"

    def __init__(self, ctx, bot, wanted_roles=None):
        super().__init__(ctx, bot, wanted_roles)
        if wanted_roles is None:
            self.wanted_roles = []
        else:
            self.wanted_roles = wanted_roles
        self.roles = []
        self.add_phase(Phase.TestDiscuss(self))
        self.add_phase(Phase.AvalonVotePhase(self))
        self.add_phase(Phase.TestDiscuss(self))



    async def game_init(self):
        try:
            if len(self.players) >= self.minimum_players:
                await self.ctx.send("Game initialized with players: ")
                await self.ctx.send(', '.join(str(p.name) for p in self.players))
                valid_channels = self.generate_channels()
                if valid_channels:
                    await self.ctx.send("Game channels are valid...")
                else:
                    return False
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

    async def feed_dm(self, message):
        await self.phases[self.current_phase_idx].feed_dm(message)

    async def generate_channels(self):
        for channel in self.guild.channels:
            if not (channel.name == 'Lobby' or channel.name == 'general'):
                channel.delete()
        # TODO create appropriate channels for game with correct permissions set up
        return False

    def help(self):
        return SacredTrophyGame.HELP_DESCRIPTION
