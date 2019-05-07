import Role
import logging
import Phase
from Game import Game
import discord
from collections import Counter

logging.basicConfig(level=logging.INFO)


class SacredTrophyGame(Game):

    minimum_players = 1

    ALL_ROLES = {'good': lambda: Role.LightServant(),
                 'bad': lambda: Role.DarkServant()}

    HELP_DESCRIPTION = "Game help: Figure it out, tough luck lol"

    CATEGORY_CHANNEL_NAME = 'Sacred Trophy Game'
    REQUIRED_VOICE_CHANNELS = {'Oracle Room': 1, 'Mirror Room': 1, 'Small Cave': 2}
    REQUIRED_TEXT_CHANNELS = {}

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
                valid_channels = await self.generate_channels()
                if valid_channels:
                    await self.ctx.send("Game channels are valid...")
                else:
                    await self.ctx.send("Game channels are invalid, or creation failed for some reason.")
                    return False
            else:
                await self.ctx.send("Game cannot start without a minimum of " + str(self.minimum_players) + " players!")
                return False
            valid, response = Role.Role.check_valid_roles(self.wanted_roles, self.ALL_ROLES)
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
        except:
            return False

    async def start_game(self):
        await super().start_game()

    async def feed_dm(self, message):
        await self.phases[self.current_phase_idx].feed_dm(message)

    async def generate_channels(self):
        if self.get_channel_by_name(SacredTrophyGame.CATEGORY_CHANNEL_NAME) is None:
            await self.guild.create_category(SacredTrophyGame.CATEGORY_CHANNEL_NAME)
        if not type(self.get_channel_by_name(SacredTrophyGame.CATEGORY_CHANNEL_NAME)) == discord.channel.CategoryChannel:
            await self.ctx.send("A channel already exists with name: \"" + SacredTrophyGame.CATEGORY_CHANNEL_NAME + "\". Could not initialize game.")
            return False
        cat = self.get_channel_by_name(SacredTrophyGame.CATEGORY_CHANNEL_NAME)
        for role in self.guild.roles:
            await cat.set_permissions(role, connect=False, mute_members=False, move_members=False)
        voices = Counter([s.name for s in cat.voice_channels])
        texts = Counter([s.name for s in cat.text_channels])
        for voice_chan_name in SacredTrophyGame.REQUIRED_VOICE_CHANNELS:
            if voice_chan_name not in voices:
                await cat.create_voice_channel(voice_chan_name)
                voices[voice_chan_name] = 1
            elif voices[voice_chan_name] < SacredTrophyGame.REQUIRED_VOICE_CHANNELS[voice_chan_name]:
                await cat.create_voice_channel(voice_chan_name)
                voices[voice_chan_name] += 1
            else:
                while voices[voice_chan_name] > SacredTrophyGame.REQUIRED_VOICE_CHANNELS[voice_chan_name]:
                    await Game.get_channel_from_category(voice_chan_name, cat).delete()
                    voices[voice_chan_name] -= 1
        for voice_chan in cat.voice_channels:
            await voice_chan.edit(sync_permissions=True)
        for text_chan_name in SacredTrophyGame.REQUIRED_TEXT_CHANNELS:
            if text_chan_name not in texts:
                await cat.create_text_channel(text_chan_name)
                texts[text_chan_name] = 1
            elif texts[text_chan_name] < SacredTrophyGame.REQUIRED_TEXT_CHANNELS[text_chan_name]:
                await cat.create_text_channel(text_chan_name)
                texts[text_chan_name] += 1
            else:
                while texts[text_chan_name] > SacredTrophyGame.REQUIRED_TEXT_CHANNELS[text_chan_name]:
                    await Game.get_channel_from_category(text_chan_name, cat).delete()
                    texts[text_chan_name] -= 1
        return True

    def help(self):
        return SacredTrophyGame.HELP_DESCRIPTION
