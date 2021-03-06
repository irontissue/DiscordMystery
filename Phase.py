import asyncio
import random
import globals
from SacredTrophyGame import SacredTrophyGame
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
        #     await member.move_to(self.parent_game.starting_room)


class SacredTrophyInfoPhase(Phase):

    def __init__(self, parent_game):
        if parent_game.oracle_mirror_rooms_size == 1:
            super().__init__(parent_game, "Info Phase", "One player has been sent to the Oracle Room. One has been"
                                                        " sent to the Mirror Room.", 20)
        else:
            super().__init__(parent_game, "Info Phase", f"{parent_game.oracle_mirror_rooms_size} players have been sent"
                                                        f" to the Oracle Room. {parent_game.oracle_mirror_rooms_size} "
                                                        f"have been sent to the Mirror Room.", 20)

    async def begin_phase(self):
        await super().begin_phase()
        rand_idxs = random.sample(list(range(len(self.parent_game.roles))), self.parent_game.oracle_mirror_rooms_size * 2)
        to_oracle = 0
        self.parent_game.phases.append(SacredTrophyGatheringPhase(self.parent_game, 0))
        for rand in rand_idxs:
            if to_oracle < len(rand_idxs) // 2:
                print(f"Moving {self.parent_game.roles[rand].member} to Oracle Room")
                await self.parent_game.roles[rand].member.move_to(self.parent_game.get_channel_by_name("Oracle Room"))
                rest = list(range(len(self.parent_game.roles)))
                rest.remove(rand)
                rand_knowledge = random.sample(rest, 1) # len(rand_idxs) // 2)
                for aa in rand_knowledge:
                    await self.parent_game.roles[rand].member.send(f"The oracle reveals to you that {self.parent_game.roles[aa].member.name} is a {self.parent_game.roles[aa].name}.")
            else:
                print(f"Moving {self.parent_game.roles[rand].member} to Mirror Room")
                await self.parent_game.roles[rand].member.move_to(self.parent_game.get_channel_by_name("Mirror Room"))
                await self.parent_game.roles[rand].member.send(f"As you peer into the mirror, you learn your true "
                                                               f"identity: {self.parent_game.roles[rand].name}.")
            to_oracle += 1

    async def start_timer(self):
        await super().start_timer()


class SacredTrophyGatheringPhase(Phase):

    def __init__(self, parent_game, num_cave_phases_completed):
        super().__init__(parent_game, "Gathering Phase", f"You have 3 minutes to vote for "
                                                         f"{parent_game.trophy_room_size} people who you would want "
                                                         f"to go to the trophy room. Send a list of {parent_game.trophy_room_size} numbers "
                                                         f"(separated by spaces). Send \"cave\" in order to end the phase and"
                                                         f" force everyone to go to a cave phase.", 180)
        self.votes = dict()
        self.voted_people = set()
        self.timed_out = True
        self.went_to_trophy = False
        self.num_cave_phases_completed = num_cave_phases_completed
        self.must_vote = False
        if num_cave_phases_completed >= SacredTrophyGame.MAX_NUM_CAVE_PHASES:
            self.duration = 0
            self.must_vote = True
        for member in self.parent_game.players:
            self.votes[member] = 0
        self.just_names = [s.name for s in self.parent_game.players]

    async def begin_phase(self):
        members = ""
        members += self.description + "\n"
        for idx in range(len(self.just_names)):
            members += f"{idx + 1} = {self.just_names[idx]}\n"
        await super().begin_phase()
        gathering = self.parent_game.get_channel_by_name("Gathering Area")
        print(self.votes)
        for member in self.votes:
            await member.move_to(gathering)
            await member.send(members)
            print(f"Sending members list to {member}")

    async def start_timer(self):
        while self.duration <= 0 or self.current_time < self.duration:
            if self.phase_over:
                break
            self.current_time += 1
            await asyncio.sleep(1)
        self.current_time = 0
        self.phase_over = False
        if not self.went_to_trophy:
            self.parent_game.phases.append(SacredTrophyCavePhase(self.parent_game, self.num_cave_phases_completed))
        if self.phase_number is None:
            await self.parent_game.ctx.send("Phase \"" + self.name + "\" is over!")
        else:
            await self.parent_game.ctx.send("Phase " + str(self.phase_number) + " (\"" + self.name + "\") is over!")
        await self.parent_game.next_phase()

    async def feed_dm(self, message):
        print(f"Phase {self.name} received message from user {message.author}: {message.content}")
        try:
            if message.author not in self.voted_people:
                if message.content.lower().strip() == "cave":
                    if self.must_vote:
                        await message.author.send(f"You can't visit the caves more than {self.num_cave_phases_completed} times! You must give a valid vote to progress the game!")
                        return
                    else:
                        await self.parent_game.ctx.send(
                            f"{message.author.name} doesn't want to send anyone to the Trophy Room."
                            f" End of Gathering Phase.")
                        self.phase_over = True
                        self.timed_out = False
                        return
                splitty = [self.parent_game.players[int(s.strip()) - 1] for s in message.content.lower().split()]
                if len(splitty) != len(set(splitty)):
                    print(f"User {message.author} sent duplicate members in votes.")
                    await message.author.send("All of your votes must be different. Try again.")
                    # await self.parent_game.ctx.send(
                    #         f"{message.author.name} tried to send duplicates to the Trophy Room."
                    #         f" End of Gathering Phase.")
                    # self.phase_over = True
                    # self.timed_out = False
                    return
                for i in range(self.parent_game.trophy_room_size):
                    if splitty[i] not in self.votes:
                        await message.author.send("Your vote was invalid. Try again.")
                        # await self.parent_game.ctx.send(
                        #     f"{message.author.name} doesn't want to send anyone to the Trophy Room."
                        #     f" End of Gathering Phase.")
                        # self.phase_over = True
                        # self.timed_out = False
                        return
                    else:
                        self.votes[splitty[i]] += 1
                self.voted_people.add(message.author)
                if len(self.voted_people) == len(self.parent_game.players):
                    await self.parent_game.ctx.send(f"The votes are in...")
                    counted = Counter(self.votes).most_common()
                    for key, val in counted:
                        await self.parent_game.ctx.send(f"{key.name}: {val}")
                    self.parent_game.phases.append(SacredTrophyTrophyPhase(self.parent_game, [ss[0] for ss in counted[:self.parent_game.trophy_room_size]]))
                    self.phase_over = True
                    self.timed_out = False
                    self.went_to_trophy = True
                    return
        except Exception as e:
            print(f"Exception in SacredTrophyGatheringPhase.feed_dm(): {e}")
            self.phase_over = True
            self.timed_out = False
            await self.parent_game.ctx.send(f"{message.author.name} doesn't want to send anyone to the Trophy Room."
                                            f"End of Gathering Phase.")


class SacredTrophyCavePhase(Phase):

    def __init__(self, parent_game, num_cave_phases_completed):
        super().__init__(parent_game, "Cave Phase", "Two players have been sent to each cave. You have 2 minutes to "
                                                    "discuss.", 60)
        self.num_cave_phases_completed = num_cave_phases_completed

    async def begin_phase(self):
        await super().begin_phase()
        rand_idxs = random.sample(list(range(len(self.parent_game.roles))), 4)
        to_cave1 = 0
        share_pool_1 = []
        share_pool_2 = []
        for rand in rand_idxs:
            if to_cave1 < len(rand_idxs) / 2:
                await self.parent_game.roles[rand].member.move_to(self.parent_game.get_channel_by_name("Small Cave"))
                share_pool_1.append(self.parent_game.roles[rand])
            else:
                await self.parent_game.roles[rand].member.move_to(self.parent_game.get_channel_by_name("Another Cave"))
                share_pool_2.append(self.parent_game.roles[rand])
            to_cave1 += 1
        # rand = random.randint(0, 1)
        # await share_pool_1[rand].member.send(f"You learn that {share_pool_1[1-rand].member.name} is a {share_pool_1[1-rand].name}.")
        # await share_pool_2[1-rand].member.send(f"You learn that {share_pool_2[rand].member.name} is a {share_pool_2[rand].name}.")
        self.parent_game.phases.append(SacredTrophyGatheringPhase(self.parent_game, self.num_cave_phases_completed + 1))


class SacredTrophyTrophyPhase(Phase):

    def __init__(self, parent_game, trophy_room_people):
        super().__init__(parent_game, "Trophy Phase", f"The {parent_game.trophy_room_size} selected players have been sent to the Trophy Room...", 0)
        self.trophy_room_people = trophy_room_people
        self.voted = set()
        self.touched = set()
        # trophy_alignment: 1 is Good. 2 is Bad.

    async def begin_phase(self):
        await super().begin_phase()
        await self.parent_game.ctx.send(self.description)
        trophy_room = self.parent_game.get_channel_by_name("Trophy Room")
        for p in self.trophy_room_people:
            await p.move_to(trophy_room)
            await p.send("Respond \"touch\" (without quotes) if you want to touch the trophy. ANY other response"
                         " means you don't touch it.")

    async def feed_dm(self, message):
        if message.author in self.trophy_room_people and message.author not in self.voted:
            self.voted.add(message.author)
            if "".join(message.content.lower().split()) == "touch":
                print(f"{message.author} typed TOUCH. Type of this player: {type(self.parent_game.get_role_by_member(message.author))}")
                await self.parent_game.ctx.send(f"{message.author.name} touched the trophy!")
                if type(self.parent_game.get_role_by_member(message.author)) == Role.LightServant:
                    self.touched.add(1)
                else:
                    self.touched.add(2)
            if len(self.voted) == self.parent_game.trophy_room_size:
                game_over = False
                if not self.touched:
                    await self.parent_game.ctx.send(f"Nobody touched the trophy! Nothing happens... The score is still "
                                              f"\nLight: {self.parent_game.good_points}, Dark: "
                                              f"{self.parent_game.bad_points}")
                elif 2 in self.touched:
                    self.parent_game.bad_points += 1
                    await self.parent_game.ctx.send(f"The trophy emits a dark aura! Score: \nLight: "
                                              f"{self.parent_game.good_points}, Dark:{self.parent_game.bad_points}")
                    if self.parent_game.bad_points == SacredTrophyGame.POINTS_TO_WIN:
                        game_over = True
                        await self.parent_game.ctx.send(f"The world is shrouded in shadows; the Dark has won!")
                else:
                    self.parent_game.good_points += 1
                    await self.parent_game.ctx.send(f"The trophy glimmers momentarily with light! Score: \nLight: "
                                              f"{self.parent_game.good_points}, Dark:{self.parent_game.bad_points}")
                    if self.parent_game.good_points == SacredTrophyGame.POINTS_TO_WIN:
                        game_over = True
                        await self.parent_game.ctx.send(f"A heavenly ray shines from above; the Light has won!")
                if not game_over:
                    self.parent_game.phases.append(SacredTrophyInfoPhase(self.parent_game))
                    self.phase_over = True
                else:
                    for member in self.parent_game.players:
                        member.move_to(self.parent_game.starting_room)
