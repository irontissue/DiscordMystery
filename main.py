from discord.ext import commands
import logging
from Game import Game

logging.basicConfig(level=logging.INFO)

TOKEN = 'NTYwNTQyMjY4MjUxOTYzNDAy.D31dcA.BF8HIB6fvbY2uizuBfJDTSExk50'

bot = commands.Bot(command_prefix='!', description='Discord Mystery Bot Controller')


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def start_game(ctx, roles):
    x = Game(ctx, bot, roles)
    await x.start_game(ctx)


bot.run(TOKEN)
