import asyncio
from random import randint
import globals


# A phase has a name, duration (seconds), and a reference to its Game that it is a part of. phase_number is given to it
# just for making printing purposes easier. phase_over puts a manual end to the phase, if some other condition
# is fulfilled that marks the end of this phase.
# Setting duration <= 0 will make the phase last indefinitely (or until it is manually ended through phase_over = True)
class Phase:

    def __init__(self, parent_game, name, description, duration):
        self.name = name
        self.description = description
        self.duration = duration
        self.current_time = 0
        self.parent_game = parent_game
        self.phase_number = None
        self.phase_over = False

    async def begin_phase(self):
        globals.add_game_task(self.parent_game.bot.loop.create_task(self.start_timer()))

    async def start_timer(self):
        while self.duration <= 0 or self.current_time < self.duration:
            if self.phase_over:
                break
            self.current_time += 1
            await asyncio.sleep(1)
        self.current_time = 0
        if self.phase_number is not None:
            await self.parent_game.ctx.send("Phase \"" + self.name + "\" is over!")
        else:
            await self.parent_game.ctx.send("Phase " + str(self.phase_number) + " (\"" + self.name + "\") is over!")
        await self.parent_game.next_phase()

    async def feed_dm(self, message):
        print(f"Phase {self.name} received message from user {message.author}: {message.content}")


class AvalonVotePhase(Phase):

    def __init__(self, parent_game):
        super().__init__(parent_game, "Vote", "Respond \"Y\" if you think this is a good mission. Any other response"
                                              "will be treated as NO.", 0)
        self.votes = {}

    async def begin_phase(self):
        await super().begin_phase()
        for member in self.parent_game.players:
            await member.send(self.description)

    async def start_timer(self):
        while len(self.votes) < len(self.parent_game.players):
            await asyncio.sleep(1)
        await self.parent_game.ctx.send(f"The votes are in... {self.votes}")
        await self.parent_game.next_phase()

    async def feed_dm(self, message):
        if message.author.name not in self.votes:
            r = message.content.lower()
            self.votes[message.author.name] = True if r == "y" else False


class FiveMinuteDiscuss(Phase):

    def __init__(self, parent_game):
        super().__init__(parent_game, "Five Minute Discussion", "Discuss the state of the game for 5 minutes,"
                                                                "then the next phase begins.", 300)


class TestDiscuss(Phase):

    def __init__(self, parent_game):
        super().__init__(parent_game, "Test 20 Second Phase", "Test", 20)

    async def begin_phase(self):
        await super().begin_phase()
        for member in self.parent_game.players:
            guild = self.parent_game.guild
            randVC = randint(1, len(guild.voice_channels) - 1)
            await self.parent_game.ctx.send(f"Moving {member.name} to {guild.voice_channels[randVC]}.")
            await member.move_to(self.parent_game.get_channel_by_name(str(guild.voice_channels[randVC])))

    async def start_timer(self):
        await super().start_timer()
        for member in self.parent_game.players:
            await member.move_to(self.parent_game.get_channel_by_name("Lobby"))
