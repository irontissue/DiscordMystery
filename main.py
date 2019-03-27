import discord
from discord.ext import commands
import logging
import random

logging.basicConfig(level=logging.INFO)

TOKEN = 'NTYwNTQyMjY4MjUxOTYzNDAy.D31dcA.BF8HIB6fvbY2uizuBfJDTSExk50'

client = discord.Client()
bot = commands.Bot(command_prefix='!', description='Discord Mystery Bot Controller')


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@client.event
async def on_message(message):
    if message.author == client.user:
        print("aa")
        return

    if message.content.startsWith('hello'):
        await message.channel.send('Hello idiot!')




bot.run(TOKEN)
