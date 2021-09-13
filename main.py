import logging
import os
import sys
import traceback
from itertools import cycle

import discord
from discord.ext import commands, tasks

# Log information about bot operations.
logging.basicConfig(level=logging.INFO)

# Get Discord token from environmental variable.
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Google Maps API token for searching places
GOOGLE_API_TOKEN = os.getenv("GOOGLE_API_TOKEN")

# Default prefix for bot commands.
DEFAULT_PREFIX = "."

# Discord message length limit.
MSG_CHAR_LIMIT = 2000

# Path to file tracking number of Google API requests.
REQUESTS_COUNTER_FILE = "data/google_api_requests.txt"

# Set the bot client with '.' (dot) as a command prefix.
pomelo_client = commands.Bot(command_prefix=DEFAULT_PREFIX)

# Status text to be displayed in bot description.
statuses = cycle(
    (
        "Powered by fruit energy!",
        "Fresh, ripe and juicy!",
        "Don't trust Pancake!",
        "Completely insect-free!",
        'Type: ".help"!',
    )
)


# Simple exception for raising when input is too heavy to handle by the bot.
class RoughInputException(Exception):
    pass


async def send_with_buffer(ctx, message_entries: list, separator="\n", message_block_indicator="```"):
    buffer = ""
    for index, entry in enumerate(message_entries):
        # Ensure 'entry' is a string so it can be concatenated.
        entry = str(entry)
        # When the buffer exceeds max character limit, dump the contents of the buffer into the message.
        if len(message_block_indicator + buffer + entry + separator + message_block_indicator) >= MSG_CHAR_LIMIT:
            await ctx.send(message_block_indicator + buffer + message_block_indicator)
            buffer = ""

        buffer = buffer + entry
        if index != len(message_entries) - 1:
            buffer += separator

    await ctx.send(message_block_indicator + buffer + message_block_indicator)


# EVENT LISTENERS


@pomelo_client.event
async def on_ready():
    """If the bot is ready (i.e. is turned on), print out the message to console."""
    change_status.start()
    print("[ONLINE] Pomelo is fresh and ripe, lads!")


@pomelo_client.event
async def on_command_error(ctx, error):
    """If user forgets to put necessary arguments into a command, mock them."""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "You're okay there pal? Because you've _clearly_ missed some of the arguments in your command... "
            "_shakes head_ Type '.help <command_name> to learn more about command."
        )
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(
            "Are you delusional? Such command **doesn't exist** AT ALL. Type '.help' if you are feeling little _stale_."
        )
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "You do not have permissions to use such command. Do not try to be tricky with me, kid."
        )
    elif isinstance(error, commands.NotOwner):
        await ctx.send(
            "Only The Creator Himself can call such spells on me."
        )

    # All other Exceptions not returned come here and the default traceback is then printed.
    print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


# LOOPS


@tasks.loop(seconds=15)
async def change_status():
    """Change status text every X seconds."""
    await pomelo_client.change_presence(activity=discord.Game(next(statuses)))


if __name__ == "__main__":
    """Check 'cogs' directory for cog files (which are basically bot modules) and load them."""
    for filename in os.listdir("cogs"):
        if filename.endswith("py"):
            pomelo_client.load_extension(f"cogs.{filename[:-3]}")

    pomelo_client.run(DISCORD_BOT_TOKEN)
