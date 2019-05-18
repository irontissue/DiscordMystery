from discord.ext import commands
import Role
import logging
import globals
import discord

logging.basicConfig(level=logging.INFO)


class Game:

    minimum_players = 1

    HELP_DESCRIPTION = "Test Game."

    def __init__(self, ctx, bot, wanted_roles):
        self.bot = bot
        self.ctx = ctx
        self.phases = []
        self.roles = []
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
        except Exception as e:
            print(f"Exception in Game.game_init: {e}")
            return False

    async def start_game(self):
        await self.phases[self.current_phase_idx].begin_phase()

    def get_member_by_name(self, name):
        try:
            for member in self.players:
                if member.name.lower() == name.lower():
                    return member
            return None
        except Exception as e:
            print(e)
            return None

    # Returns channel given the name.
    def get_channel_by_name(self, name):
        for channel in self.guild.channels:
            if channel.name.lower() == name.lower():
                return channel
        return None

    def get_role_by_member(self, member):
        for role in self.roles:
            if role.member == member:
                return role
        return None

    def get_role_by_member_name(self, name):
        for role in self.roles:
            if role.member.name.lower() == name.lower():
                return role
        return None

    # Returns channel given the name, from given category channel.
    @staticmethod
    def get_channel_from_category(name, cat):
        if type(cat) != discord.channel.CategoryChannel:
            print(f"ERROR: get_channel_from_category was incorrectly given a {type(cat)} as input.")
        for channel in cat.channels:
            if channel.name.lower() == name.lower():
                return channel
        return None

    def add_phase(self, phase):
        phase.parent_game = self
        phase.phase_number = len(self.phases) + 1
        self.phases.append(phase)

    async def next_phase(self):
        self.current_phase_idx += 1
        if self.current_phase_idx >= len(self.phases):
            await self.ctx.send("The game is over.")
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
