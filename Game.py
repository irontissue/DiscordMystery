from discord.ext import commands
import Role
import logging
import globals

logging.basicConfig(level=logging.INFO)


class Game:

    minimum_players = 1

    HELP_DESCRIPTION = "Test Game."

    def __init__(self, ctx, bot, wanted_roles):
        self.bot = bot
        self.ctx = ctx
        self.phases = []
        self.current_phase_idx = 0
        self.guild = self.bot.get_guild(self.ctx.guild.id)
        lobby = self.get_channel_by_name('Lobby')
        self.players = lobby.members

    async def game_init(self):
        try:
            if len(self.players) >= self.minimum_players:
                await self.ctx.send("Game initialized with players: ")
                await self.ctx.send(', '.join(str(p.name) for p in self.players))
                valid_channels = self.generate_channels()
                if valid_channels:
                    await self.ctx.send("Game channels have been created...")
                else:
                    await self.ctx.send("Game channels could not be initialized properly.")
                    return False
                return True
            else:
                await self.ctx.send("Game cannot start without a minimum of " + str(self.minimum_players) + " players!")
                return False
        except:
            return False

    async def start_game(self):
        await self.phases[self.current_phase_idx].begin_phase()

    def get_channel_by_name(self, name):
        for channel in self.guild.channels:
            if channel.name == name:
                return channel
        return None

    def add_phase(self, phase):
        phase.parent_game = self
        phase.phase_number = len(self.phases) + 1
        self.phases.append(phase)

    async def next_phase(self):
        self.current_phase_idx += 1
        if self.current_phase_idx >= len(self.phases):
            await self.ctx.send("Game is over haha lol")
            globals.current_game = None
        else:
            await self.phases[self.current_phase_idx].begin_phase()

    async def feed_dm(self, message):
        # print(f"Got DM from {message.author}: {message.content}")
        return

    async def feed_message(self, message):
        # print(f"{message}")
        return

    def generate_channels(self):
        return True

    def help(self):
        return Game.HELP_DESCRIPTION
