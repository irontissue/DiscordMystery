import discord
from discord.ext import commands
import logging
import random

logging.basicConfig(level=logging.INFO)

TOKEN = 'NTYwNTQyMjY4MjUxOTYzNDAy.D31dcA.BF8HIB6fvbY2uizuBfJDTSExk50'

bot = commands.Bot(command_prefix='!', description='Discord Mystery Bot Controller')


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


# 560612701412392970
@bot.command()
async def start_game(ctx):
    channel_name = "Lobby"
    lobby_id, lobby = get_channel_by_name(channel_name)
    for member in lobby.members:
        await ctx.send("Moving " + str(member) + " to Ballroom.")
        await member.move_to(get_channel_by_name("Ballroom")[1])


def get_channel_by_name(name):
    for channel in bot.get_all_channels():
        if channel.name == name:
            return channel.id, channel


bot.run(TOKEN)
