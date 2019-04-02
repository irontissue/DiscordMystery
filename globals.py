import asyncio

# Global variables that need to be used by various files

# If you want to "end" the game, just set this back to None from anywhere and main.py should handle the rest of it
current_game = None
all_game_tasks = set()


def add_game_task(task):
    all_game_tasks.add(task)


async def end_all_game_tasks():
    remove_set = set()
    for task in all_game_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            remove_set.add(task)
    for task in remove_set:
        all_game_tasks.remove(task)


def print_tasks():
    for task in all_game_tasks:
        print(f"{task}")
