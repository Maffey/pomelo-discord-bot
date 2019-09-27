import json
import shelve
import time

import discord
from discord.ext import commands


class Mod(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['changeprefix'])
    @commands.has_permissions(administrator=True)
    async def change_prefix(self, ctx, new_prefix):
        with open('/home/ubuntu/PomeloDiscordBot/data/prefixes.json', 'r') as json_file:
            prefixes = json.load(json_file)

        prefixes[str(ctx.guild.id)] = new_prefix

        with open('/home/ubuntu/PomeloDiscordBot/data/prefixes.json', 'w') as json_file:
            json.dump(prefixes, json_file, indent=4)

        await ctx.send(f'Prefix has been changed to "{new_prefix}"')

    @commands.command(description='Clear the given amount of messages from the chat.')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=3):
        amount += 2
        await ctx.send(
            '**snap** https://media1.tenor.com/images/e36fb32cfc3b63075adf0f1843fdc43a/tenor.gif?itemid=12502580')
        time.sleep(1.8)
        await ctx.channel.purge(limit=amount)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        print(f'The user {member} has been kicked.')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        print(f'The user {member} has been banned.')

    @commands.command(description='Unbans the given user.')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()  # Gets list of banned users from the server.
        # Splits the username to his name and discriminator (Discord user's ID)
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                print(f'Unbanned {user}')

    @commands.command(description='Loads the given Cog.')
    @commands.has_permissions(administrator=True)
    async def load(self, ctx, extension):
        self.client.load_extension(f'cogs.{extension}')
        await ctx.send(f'The "{extension.upper()}" Cog has been loaded.')

    @commands.command(description='Reloads the given Cog.')
    @commands.has_permissions(administrator=True)
    async def reload(self, ctx, extension):
        self.client.unload_extension(f'cogs.{extension}')
        self.client.load_extension(f'cogs.{extension}')
        await ctx.send(f'The "{extension.upper()}" Cog has been reloaded.')

    @commands.command(description='Unloads the given Cog.')
    @commands.has_permissions(administrator=True)
    async def unload(self, ctx, extension):
        self.client.unload_extension(f'cogs.{extension}')
        await ctx.send(f'The "{extension.upper()}" Cog has been unloaded.')

    @commands.command(aliases=['addmeme'], description='Adds the given meme to the meme database.')
    async def add_meme(self, ctx, hyperlink, *, keyword):
        # Place the meme in the shelf object. Overwriting existing meme is possible. Optionally, add defensive
        # strategy later.
        with shelve.open('/home/ubuntu/PomeloDiscordBot/data/memes_shelf') as memes_shelf:
            memes_shelf[keyword] = {'hyperlink': hyperlink, 'description': 'new meme', 'frequency': 0}
            await ctx.send('The meme has been added.')

    @commands.command(aliases=['delmeme'], description='Removes the meme from the meme database.')
    @commands.has_permissions(administrator=True)
    async def del_meme(self, ctx, *, keyword):
        # Remove the meme from shelf object.
        with shelve.open('/home/ubuntu/PomeloDiscordBot/data/memes_shelf') as memes_shelf:
            del memes_shelf[keyword]
            await ctx.send('The meme has been removed.')

    @commands.command(aliases=['changedes'])
    @commands.has_permissions(administrator=True)
    async def change_meme_description(self, ctx, keyword, *, description):

        keyword = keyword.lower()
        keyword = keyword.replace('-', ' ')
        keyword = keyword.replace('_', ' ')

        with shelve.open('/home/ubuntu/PomeloDiscordBot/data/memes_shelf') as memes_shelf:
            # figure out how to add help here
            try:
                # Open up the meme.
                meme_dict = memes_shelf[keyword]
            except KeyError:
                await ctx.send('No such meme exists. You messed up!')

            meme_dict = {'hyperlink': meme_dict['hyperlink'], 'description': str(description),
                         'frequency': meme_dict['frequency']}
            memes_shelf[keyword] = meme_dict
        await ctx.send(f'The description of | **{keyword}** | has been changed to *"{description}"*.')


def setup(client):
    client.add_cog(Mod(client))
