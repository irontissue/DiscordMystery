from discord.ext import commands
import logging

logging.basicConfig(level=logging.INFO)


class Game:

    minimum_players = 1

    def __init__(self, ctx, bot, roles):
        self.bot = bot
        self.channels = list(bot.get_all_channels())
        lobby = self.get_channel_by_name('Lobby')
        self.players = lobby.members

    async def start_game(self, ctx):
        if len(self.players) >= self.minimum_players:
            await ctx.send("Game started with players: ")
            await ctx.send(', '.join(str(p.name) for p in self.players))
            await ctx.send("Game started with channels: ")
            await ctx.send(', '.join(str(p.name) for p in self.channels))
            for member in self.players:
                await ctx.send("Moving " + str(member) + " to Ballroom.")
                await member.move_to(self.get_channel_by_name("Ballroom"))
        else:
            await ctx.send("Game cannot start without a minimum of " + str(self.minimum_players) + " players!")

    def get_channel_by_name(self, name):
        for channel in self.channels:
            if channel.name == name:
                return channel
