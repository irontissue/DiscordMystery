import asyncio


# A phase has a name, duration (seconds), and a reference to its Game that it is a part of. phase_number is given to it
# just for making printing purposes easier. phase_over puts a manual end to the phase, if some other condition
# is fulfilled that marks the end of this phase.
# Setting duration <= 0 will make the phase last indefinitely (or until it is manually ended through phase_over = True)
class Phase:

    def __init__(self, parent_game, name, duration):
        self.name = name
        self.duration = duration
        self.current_time = 0
        self.parent_game = parent_game
        self.phase_number = None
        self.phase_over = False

    async def begin_phase(self):
        self.parent_game.bot.loop.create_task(self.start_timer())

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


class FiveMinuteDiscuss(Phase):

    def __init__(self, parent_game):
        super().__init__(parent_game, "Five Minute Discussion", 300)


class TestDiscuss(Phase):

    def __init__(self, parent_game):
        super().__init__(parent_game, "Test 5 Second Phase", 5)

    async def begin_phase(self):
        await super().begin_phase()
        for member in self.parent_game.players:
            await self.parent_game.ctx.send("Moving " + str(member) + " to Ballroom.")
            await member.move_to(self.parent_game.get_channel_by_name("Ballroom"))
