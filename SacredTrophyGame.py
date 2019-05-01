import Role
import logging
import Phase
from Game import Game
import discord

logging.basicConfig(level=logging.INFO)


class SacredTrophyGame(Game):

    minimum_players = 1

    ALL_ROLES = {'good': lambda: Role.LightServant(),
                 'bad': lambda: Role.DarkServant()}

    HELP_DESCRIPTION = "Game help: Figure it out, tough luck lol"

    CATEGORY_CHANNEL_NAME = 'Sacred Trophy Game'
    REQUIRED_VOICE_CHANNELS = ['Oracle Room', 'Mirror Room', 'Small Cave', 'Small Cave']
    REQUIRED_TEXT_CHANNELS = ['general']

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
        voices = dict(zip([s.name for s in cat.voice_channels], cat.voice_channels))
        texts = dict(zip([s.name for s in cat.text_channels], cat.text_channels))
        for voice_chan in SacredTrophyGame.REQUIRED_VOICE_CHANNELS:
            if voice_chan not in voices:
                await cat.create_voice_channel(voice_chan)
                voices[voice_chan] = self.get_channel_by_name(voice_chan)
        for text_chan in SacredTrophyGame.REQUIRED_TEXT_CHANNELS:
            if text_chan not in texts:
                await cat.create_text_channel(text_chan)
                texts[text_chan] = self.get_channel_by_name(text_chan)
        return True

    def help(self):
        return SacredTrophyGame.HELP_DESCRIPTION
