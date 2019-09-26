# IMPORTS

import os
import discord
import json

from discord.ext import commands, tasks
from itertools import cycle

# Get discord token from local file
with open('/home/ubuntu/PomeloDiscordBot/data/token.json', 'r') as token_file:
    token = json.load(token_file)
    DISCORD_BOT_TOKEN = token["discord-token"]




DEFAULT_PREFIX = '.'

def get_prefix(client, message):
    with open('/home/ubuntu/PomeloDiscordBot/data/prefixes.json', 'r') as json_file:
        prefixes = json.load(json_file)

    return prefixes[str(message.guild.id)]

client = commands.Bot(command_prefix=get_prefix)  # Sets the bot to treat a dot (.) as a call for command.

statuses = cycle(
    ('Powered by AWS!', 'Fresh, ripe and juicy!', 'Don\'t trust Pancake!',
     'Completely insect-free!', 'My creator is insane!', 'Don\'t use Repl.it!'))



# EVENT LISTENERS


# While bot is ready (i.e. is turned on) it prints out the message to console.
@client.event
async def on_ready():
    change_status.start()
    print('Pomelo is fresh and ripe, lads!')


@client.event
async def on_guild_join(guild):
    with open('/home/ubuntu/PomeloDiscordBot/data/prefixes.json', 'r') as json_file:
        prefixes = json.load(json_file)

    prefixes[str(guild.id)] = DEFAULT_PREFIX

    with open('/home/ubuntu/PomeloDiscordBot/data/prefixes.json', 'w') as json_file:
        json.dump(prefixes, json_file, indent=4)


@client.event
async def on_guild_remove(guild):
    with open('/home/ubuntu/PomeloDiscordBot/data/prefixes.json', 'r') as json_file:
        prefixes = json.load(json_file)

    prefixes.pop(str(guild.id))

    with open('/home/ubuntu/PomeloDiscordBot/data/prefixes.json', 'w') as json_file:
        json.dump(prefixes, json_file, indent=4)


# When someone joins a server, print out info about who and what server they joined.
@client.event
async def on_member_join(member):
    print(f'{member} has joined the {member.guild} server.')


# When someone leaves a server, print out info about who and what server they left.
@client.event
async def on_member_remove(member):
    print(f'{member} has left the {member.guild} server.')


# When user forgets to put necessary arguments, mock them.
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You\'re okey there pal? Because you\'ve clearly missed some of the arguments in your command... ***shakes head***')
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send('Are you delusional? Such command doesn\'t exist AT ALL. Type "help" if you are a little *stale*.')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('You do not have permissions to use such command.')


# LOOPS


@tasks.loop(seconds=15)
async def change_status():
    await client.change_presence(activity=discord.Game(next(statuses)))


# Checks "cogs" folder for cog files (duh) and then loads them.
for filename in os.listdir('./cogs'):
    if filename.endswith('py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(DISCORD_BOT_TOKEN)
