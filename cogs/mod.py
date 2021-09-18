import shelve
import time
import pymongo
import discord
from discord.ext import commands

from main import REQUESTS_COUNTER_FILE, MONGODB_CONNECTION_STRING


class Mod(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(brief="Clears messages from the chat")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=3):
        amount += 2
        await ctx.send(
            "**SNAP**\nhttps://media1.tenor.com/images/e36fb32cfc3b63075adf0f1843fdc43a/tenor.gif?itemid=12502580"
        )
        time.sleep(1.8)
        await ctx.channel.purge(limit=amount)

    @commands.command(brief="Kicks selected user")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        print(f"The user {member} has been kicked.")

    @commands.command(brief="Bans selected user")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        print(f"The user {member} has been banned.")

    @commands.command(brief="Unbans selected user")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        # Get list of banned users from the server.
        banned_users = await ctx.guild.bans()
        # Split the username to his name and discriminator (Discord user's ID).
        member_name, member_discriminator = member.split("#")

        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                print(f"Unbanned {user}")

    @commands.command(brief="Loads the given Cog")
    @commands.is_owner()
    async def load(self, ctx, extension):
        self.client.load_extension(f"cogs.{extension}")
        await ctx.send(f"The '{extension.upper()}' Cog has been loaded.")

    @commands.command(brief="Reloads the given Cog")
    @commands.is_owner()
    async def reload(self, ctx, extension):
        self.client.unload_extension(f"cogs.{extension}")
        self.client.load_extension(f"cogs.{extension}")
        await ctx.send(f"The '{extension.upper()}' Cog has been reloaded.")

    @commands.command(brief="Unloads the given Cog")
    @commands.is_owner()
    async def unload(self, ctx, extension):
        self.client.unload_extension(f"cogs.{extension}")
        await ctx.send(f"The '{extension.upper()}' Cog has been unloaded.")

    @commands.command(
        aliases=["addmeme"], brief="Adds the given meme to the meme database"
    )
    @commands.has_permissions(administrator=True)
    async def add_meme(self, ctx, hyperlink, *, keyword):
        keyword = keyword.lower()
        # If the user tries to overwrite the list of memes, they are prevented..
        if keyword == "help":
            await ctx.send(
                "You cannot override the list of all the memes, you storming fool!"
            )
            return
        # TODO: Add check mechanism to prevent overwriting memes.
        with shelve.open("data/memes_shelf") as memes_shelf:
            memes_shelf[keyword] = {
                "hyperlink": hyperlink,
                "description": "**new meme**",
                "frequency": 0,
            }
            await ctx.send("The meme has been added.")

    @commands.command(
        aliases=["delmeme"], brief="Removes the meme from the meme database"
    )
    @commands.is_owner()
    async def del_meme(self, ctx, *, keyword):
        keyword = keyword.lower()
        with shelve.open("data/memes_shelf") as memes_shelf:
            if keyword in memes_shelf:
                del memes_shelf[keyword]
                await ctx.send("The meme has been removed.")
            else:
                await ctx.send("There is no such meme, what are you doin'?")

    @commands.command(
        aliases=["change_meme_description", "changedes"],
        brief="Changes meme description",
    )
    @commands.has_permissions(administrator=True)
    async def set_meme_description(self, ctx, keyword, *, description):
        keyword = keyword.lower()
        keyword = keyword.replace("-", " ")
        keyword = keyword.replace("_", " ")

        with shelve.open("data/memes_shelf") as memes_shelf:
            try:
                # Find the meme by keyword and store it in 'meme_dict' variable.
                meme_dict = memes_shelf[keyword]
            except KeyError:
                await ctx.send("No such meme exists. You messed up!")

            meme_dict = {
                "hyperlink": meme_dict["hyperlink"],
                "description": str(description),
                "frequency": meme_dict["frequency"],
            }
            memes_shelf[keyword] = meme_dict
        await ctx.send(
            f"The description of | **{keyword}** | has been changed to _'{description}'_."
        )

    @commands.command(
        aliases=["printapi"],
        brief="Print number of API requests",
        description="Print number of Google API requests. Tracked while executing places search.",
    )
    @commands.is_owner()
    async def print_api(self, ctx):
        with open(REQUESTS_COUNTER_FILE, "r") as requests_count_file:
            requests_count = int(requests_count_file.read())
        await ctx.send(
            f"Current number of Google API requests executed: **{requests_count}**"
        )

    @commands.command(
        aliases=["resetapi"],
        brief="Reset tracked number of API requests",
        description="Reset tracked number of Google API requests. Tracked while executing places search.",
    )
    @commands.is_owner()
    async def reset_api(self, ctx):
        with open(REQUESTS_COUNTER_FILE, "w") as requests_count_file:
            requests_count_file.write("0\n")
        await ctx.send("Number of Google API requests successfully reset to 0.")

    @commands.is_owner()
    @commands.command(brief="Run once.")
    async def migrate(self, ctx):
        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)

        # Create the database for our example (we will use the same database throughout the tutorial
        pomelo_db = client["pomelo_db"]
        memes_collection = pomelo_db["memes"]

        with shelve.open("data/memes_shelf") as memes_shelf:
            meme_keys = list(memes_shelf.keys())
            for key in meme_keys:
                meme_name = key
                description = memes_shelf[key]["description"]
                times_used = memes_shelf[key]["frequency"]
                url = memes_shelf[key]["hyperlink"]
                item = {
                    "name": key,
                    "description": description,
                    "times_used": times_used,
                    "url": url
                }
                memes_collection.insert_one(item)


def setup(client):
    client.add_cog(Mod(client))
