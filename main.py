from discord.ext import commands
import logging, discord
import SimpleAvalonGame
import SacredTrophyGame
import globals
import asyncio

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
    if globals.current_game is not None:
        await ctx.send("Another game is already in progress.")
    else:
        globals.current_game = SimpleAvalonGame.SimpleAvalonGame(ctx, bot, roles)
        success = await globals.current_game.game_init()
        if success:
            await globals.current_game.start_game()
        else:
            globals.current_game = None


@bot.command()
async def sacred_trophy(ctx, starting_room):
    try:
        if globals.current_game is not None:
            await ctx.send("Another game is already in progress.")
        else:
            the_channel = None
            for channel in bot.get_guild(ctx.guild.id).channels:
                if channel.name.lower() == starting_room.lower():
                    the_channel = channel
            if the_channel is None:
                await ctx.send("Invalid starting room given!")
                return
            globals.current_game = SacredTrophyGame.SacredTrophyGame(ctx, bot, the_channel)
            success = await globals.current_game.game_init()
            if success:
                await globals.current_game.start_game()
            else:
                globals.current_game = None
    except Exception as e:
        print(e)
        await ctx.send("Usage: \"sacred_trophy <starting room>\"")


@bot.command()
async def force_end(ctx):
    if globals.current_game is not None:
        await ctx.send("Force ending game.")
        await globals.end_all_game_tasks()
        globals.current_game = None


# Purely for debugging, prints all current game tasks (threads) that globals.py is keeping track of.
# @bot.command()
# async def print_tasks(ctx):
#     globals.print_tasks()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    try:
        if globals.current_game is not None and message.author in globals.current_game.players:
            if isinstance(message.channel, discord.DMChannel):
                await globals.current_game.feed_dm(message)
            else:
                await globals.current_game.feed_message(message)

        if message.channel.name == 'discordmystery':
            await bot.process_commands(message)
    except Exception as e:
        print(f"Exception in main.on_message: {e}")


@bot.event
async def on_command_error(ctx, error):
    await ctx.send(error)
    print(error)


print(TOKEN)
bot.run(TOKEN)
