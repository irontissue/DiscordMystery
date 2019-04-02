from discord.ext import commands
import logging, discord
from SimpleAvalonGame import SimpleAvalonGame

logging.basicConfig(level=logging.INFO)

with open('token', 'r') as file:
    TOKEN = str(file.read())


bot = commands.Bot(command_prefix="!", status=discord.Status.idle, activity=discord.Game(name="Booting..."))


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="Active!"))
    print('------')


@bot.command()
async def start_game(ctx, *roles):
    x = SimpleAvalonGame(ctx, bot, roles)
    success = await x.game_init()
    if success:
        await x.start_game()


print(TOKEN)
bot.run(TOKEN)
