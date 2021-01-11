# IMPORTS

import json
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

# Default prefix for bot commands.
DEFAULT_PREFIX = "."

pomelo_client = commands.Bot(command_prefix=DEFAULT_PREFIX)  # Sets the bot to treat a dot (.) as a call for command.

statuses = cycle(
    ("Powered by fruit energy!", "Fresh, ripe and juicy!", "Don't trust Pancake!",
     "Completely insect-free!", "Keep your pomelos salt-free!"))


# EVENT LISTENERS


# While bot is ready (i.e. is turned on) it prints out the message to console.
@pomelo_client.event
async def on_ready():
    change_status.start()
    print("Pomelo is fresh and ripe, lads!")


@pomelo_client.event
async def on_guild_join(guild):
    with open("data/prefixes.json", "r") as json_file:
        prefixes = json.load(json_file)

    prefixes[str(guild.id)] = DEFAULT_PREFIX

    with open("data/prefixes.json", "w") as json_file:
        json.dump(prefixes, json_file, indent=4)


@pomelo_client.event
async def on_guild_remove(guild):
    with open("data/prefixes.json", "r") as json_file:
        prefixes = json.load(json_file)

    prefixes.pop(str(guild.id))

    with open("data/prefixes.json", "w") as json_file:
        json.dump(prefixes, json_file, indent=4)


# When someone joins a server, print out info about who and what server they joined.
@pomelo_client.event
async def on_member_join(member):
    print(f"{member} has joined the {member.guild} server.")


# When someone leaves a server, print out info about who and what server they left.
@pomelo_client.event
async def on_member_remove(member):
    print(f"{member} has left the {member.guild} server.")


# When user forgets to put necessary arguments, mock them.
@pomelo_client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "You're okay there pal? Because you've _clearly_ missed some of the arguments in your command... "
            "_shakes head_")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(
            "Are you delusional? Such command **doesn't exist** AT ALL. Type 'help' if you are feeling little _stale_.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permissions to use such command. Do not try to be tricky with me.")

    # All other Errors not returned come here... And we can just print the default traceback.
    print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


# LOOPS


@tasks.loop(seconds=15)
async def change_status():
    await pomelo_client.change_presence(activity=discord.Game(next(statuses)))


# Checks "cogs" folder for cog files (duh) and then loads them.
for filename in os.listdir("cogs"):
    if filename.endswith("py"):
        pomelo_client.load_extension(f"cogs.{filename[:-3]}")

pomelo_client.run(DISCORD_BOT_TOKEN)
