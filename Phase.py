import asyncio
import random
import globals
from collections import Counter
import Role


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
        self.phase_over = False
        if self.phase_number is None:
            await self.parent_game.ctx.send("Phase \"" + self.name + "\" is over!")
        else:
            await self.parent_game.ctx.send("Phase " + str(self.phase_number) + " (\"" + self.name + "\") is over!")
        await self.parent_game.next_phase()

    async def feed_dm(self, message):
        print(f"Phase {self.name} received message from user {message.author}: {message.content}")


class AvalonVotePhase(Phase):

    def __init__(self, parent_game):
        super().__init__(parent_game, "Vote", "Respond \"Y\" if you think this is a good mission. Any other response"
                                              " will be treated as NO.", 0)
        self.votes = dict()

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
        # for member in self.parent_game.players:
        #     guild = self.parent_game.guild
        #     randVC = randint(1, len(guild.voice_channels) - 1)
        #     await self.parent_game.ctx.send(f"Moving {member.name} to {guild.voice_channels[randVC]}.")
        #     await member.move_to(self.parent_game.get_channel_by_name(str(guild.voice_channels[randVC])))

    async def start_timer(self):
        await super().start_timer()
        # for member in self.parent_game.players:
        #     await member.move_to(self.parent_game.get_channel_by_name("Lobby"))


class SacredTrophyInfoPhase(Phase):

    def __init__(self, parent_game):
        super().__init__(parent_game, "Info Phase", "Two players have been sent to the Oracle Room. Two have been"
                                                    " sent to the Mirror Room", 30)

    async def begin_phase(self):
        await super().begin_phase()
        rand_idxs = random.sample(range(len(self.parent_game.roles)), 4)
        to_oracle = 0
        for rand in rand_idxs:
            if to_oracle < 2:
                await self.parent_game.roles[rand].member.move_to(self.parent_game.get_channel_by_name("Oracle Room"))
            else:
                await self.parent_game.roles[rand].member.move_to(self.parent_game.get_channel_by_name("Mirror Room"))
            to_oracle += 1

    async def start_timer(self):
        await super().start_timer()


class SacredTrophyGatheringPhase(Phase):

    def __init__(self, parent_game):
        super().__init__(parent_game, "Gathering Phase", "You have 5 minutes to vote for 3 people who you would want"
                                                         " to go to the trophy room. Send me a list of 3 people "
                                                         "(separated by commas). An invalid response will be treated"
                                                         " as \"pass\".", 300)
        self.votes = dict()
        self.voted_people = set()
        for member in self.parent_game.players:
            self.votes[member] = 0

    async def begin_phase(self):
        await super().begin_phase()
        gathering = self.parent_game.get_channel_by_name("Gathering Area")
        for member in self.parent_game.players:
            await member.move_to(gathering)
            await member.send(self.description)

    async def start_timer(self):
        await super().start_timer()

    async def feed_dm(self, message):
        try:
            if message.author not in self.voted_people:
                self.voted_people.add(message.author)
                splitty = message.content.lower().split(',')
                for split in splitty:
                    if split.strip() not in self.votes:
                        await self.parent_game.ctx.send(
                            f"{message.author.name} doesn't want to send anyone to the Trophy Room."
                            f" End of Gathering Phase.")
                        self.phase_over = True
                        self.parent_game.phases.append(SacredTrophyCavePhase(self.parent_game))
                    else:
                        self.votes[self.parent_game.get_member_by_name(split.strip())] += 1
            if len(self.voted_people) == len(self.parent_game.players):
                await self.parent_game.ctx.send(f"The votes are in...")
                counted = Counter(self.votes).most_common()
                for key, val in counted:
                    await self.parent_game.ctx.send(f"{key.name}: {val}")
                self.parent_game.phases.append(SacredTrophyTrophyPhase(self.parent_game, [counted[0][0], counted[1][0], counted[2][0]]))
                self.phase_over = True
        except Exception as e:
            print(f"Exception in SacredTrophyGatheringPhase.feed_dm(): {e}")
            self.phase_over = True
            await self.parent_game.ctx.send(f"{message.author.name} doesn't want to send anyone to the Trophy Room."
                                            f"End of Gathering Phase.")
            self.parent_game.phases.append(SacredTrophyCavePhase(self.parent_game))


class SacredTrophyCavePhase(Phase):

    def __init__(self, parent_game):
        super().__init__(parent_game, "Cave Phase", "Two players have been sent to each cave. You have 2 minutes to "
                                                    "discuss.", 120)


class SacredTrophyTrophyPhase(Phase):

    def __init__(self, parent_game, trophy_room_people):
        super().__init__(parent_game, "Trophy Phase", "The 3 selected players have been sent to the Trophy Room...", 0)
        self.trophy_room_people = trophy_room_people
        self.voted = set()
        self.num_touched = 0
        # trophy_alignment: 0 is neutral (nobody touched it). 1 is Good. 2 is Bad.
        self.trophy_alignment = 0

    async def begin_phase(self):
        await super().begin_phase()
        await self.parent_game.ctx.send(f"Sending {self.trophy_room_people[0]}, {self.trophy_room_people[1]}, and"
                                        f" {self.trophy_room_people[2]} to the Trophy Room!")
        trophy_room = self.parent_game.get_channel_by_name("Trophy Room")
        for p in self.trophy_room_people:
            await p.move_to(trophy_room)
            await p.send("Respond \"touch\" without the quotes if you want to touch the trophy. Any other response"
                         "means you don't touch it.")

    async def feed_dm(self, message):
        if message.author in self.trophy_room_people and message.author not in self.voted:
            self.voted
            if "".join(message.content.lower().split()) == "touch":
                if type(self.parent_game.get_role_by_member(message.author)) == Role.LightServant:
