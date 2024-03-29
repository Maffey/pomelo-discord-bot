import asyncio
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

# MongoDB connection string
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")

# Default prefix for bot commands.
DEFAULT_PREFIX = "."

# Path to file tracking number of Google API requests.
REQUESTS_COUNTER_FILE = "data/google_api_requests.txt"  # todo

# Set the bot client with '.' (dot) as a command prefix.
# TODO: the hell are intents?
POMELO_CLIENT = commands.Bot(
    intents=discord.Intents.all(), command_prefix=DEFAULT_PREFIX
)

# Status text to be displayed in bot description.
STATUS_LIST = cycle(
    (
        "Powered by fruit energy.",
        "Fresh, ripe and juicy.",
        "Don't trust Pancake!",
        "Completely insect-free!",
        'Type: ".help"',
    )
)


# EVENT LISTENERS


@POMELO_CLIENT.event
async def on_ready():
    """If the bot is ready (i.e. is turned on), print out the message to console."""
    change_status.start()
    print("[ONLINE] Pomelo is fresh and ripe, lads!")


@POMELO_CLIENT.event
async def on_command_error(ctx, error):
    """If user forgets to put necessary arguments into a command, mock them."""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "You're okay there pal? Because you've _clearly_ missed "
            "some of the arguments in your command... "
            "_shakes head_ Type '.help <command_name> to learn more about command."
        )
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(
            "Are you delusional? Such command **doesn't exist** AT ALL. "
            "Type '.help' if you are feeling little _stale_."
        )
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "You do not have permissions to use such command. "
            "Do not try to be tricky with me, kid."
        )
    elif isinstance(error, commands.NotOwner):
        await ctx.send("Only The Creator Himself can call such spells on me.")

    # All other Exceptions not returned come here
    # and the default traceback is then printed.
    print(f"Ignoring exception in command {ctx.command}: ", file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


# LOOPS


@tasks.loop(seconds=15)
async def change_status():
    """Change status text every X seconds."""
    await POMELO_CLIENT.change_presence(activity=discord.Game(next(STATUS_LIST)))


async def load_extensions():
    """Check 'cogs' directory for cog files (which are basically bot modules) "
    "and load them."""
    for filename in os.listdir(os.path.join("src", "cogs")):
        if filename.endswith(".py"):
            await POMELO_CLIENT.load_extension(f"cogs.{filename[:-3]}")


async def main():
    async with POMELO_CLIENT:
        await load_extensions()
        await POMELO_CLIENT.start(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[HALT] Shutting down manually.")
