from discord.ext import commands
import Role
import logging

logging.basicConfig(level=logging.INFO)


class Game:

    minimum_players = 1

    def __init__(self, ctx, bot, wanted_roles):
        self.bot = bot
        self.ctx = ctx
        self.channels = list(bot.get_all_channels())
        lobby = self.get_channel_by_name('Lobby')
        self.players = lobby.members
        self.phases = []
        self.current_phase = 0

    async def game_init(self):
        try:
            if len(self.players) >= self.minimum_players:
                await self.ctx.send("Game initialized with players: ")
                await self.ctx.send(', '.join(str(p.name) for p in self.players))
                await self.ctx.send("Game initialized with channels: ")
                await self.ctx.send(', '.join(str(p.name) for p in self.channels))
                return True
            else:
                await self.ctx.send("Game cannot start without a minimum of " + str(self.minimum_players) + " players!")
                return False
        except:
            return False

    async def start_game(self):
        await self.phases[self.current_phase].begin_phase()

    def get_channel_by_name(self, name):
        for channel in self.channels:
            if channel.name == name:
                return channel

    def add_phase(self, phase):
        phase.parent_game = self
        phase.phase_number = len(self.phases) + 1
        self.phases.append(phase)

    async def next_phase(self):
        self.current_phase += 1
        if self.current_phase >= len(self.phases):
            await self.ctx.send("Game is over haha lol")
        else:
            await self.phases[self.current_phase].begin_phase()
