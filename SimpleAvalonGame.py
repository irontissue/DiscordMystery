from discord.ext import commands
import Role
import logging
import Phase
from Game import Game
import discord

logging.basicConfig(level=logging.INFO)


# This game doesn't work at all yet. Just used for testing with familiar names we know from Resistance: Avalon.
# Use this as an example reference for making other games
class SimpleAvalonGame(Game):

    minimum_players = 1

    ALL_ROLES = {'merlin': Role.Merlin,
                 'mordred': Role.Mordred,
                 'oberon': Role.Oberon,
                 'morgana': Role.Morgana,
                 'percival': Role.Percival,
                 'loyal servant': Role.LoyalServant,
                 'minion of mordred': Role.MinionOfMordred,
                 'good': Role.LoyalServant,
                 'bad': Role.MinionOfMordred}

    CATEGORY_CHANNEL_NAME = 'Simple Avalon Game'
    REQUIRED_VOICE_CHANNELS = {'Room': 1}
    REQUIRED_TEXT_CHANNELS = {'general': 1}

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
                    await self.ctx.send("Game channels are invalid.")
                    return False
            else:
                await self.ctx.send("Game cannot start without a minimum of " + str(self.minimum_players) + " players!")
                return False
            valid, response = Role.Role.check_valid_roles(self.wanted_roles, self.ALL_ROLES, len(self.players))
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
        except Exception as e:
            print(f"Exception in SimpleAvalonGame.game_init: {e}")
            return False

    async def start_game(self):
        await super().start_game()

    async def feed_dm(self, message):
        await self.phases[self.current_phase_idx].feed_dm(message)

    def generate_channels(self):
        return True
