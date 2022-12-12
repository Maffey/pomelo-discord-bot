import time

import discord
from discord.ext import commands

from utilities import (
    insert_meme,
    get_collection,
    update_meme,
    get_meme,
    delete_meme,
    get_api,
    reset_api,
)


class Mod(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(brief="Clears messages from the chat")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=3):
        amount += 2
        await ctx.send(
            "**SNAP**\nhttps://media1.tenor.com/"
            "images/e36fb32cfc3b63075adf0f1843fdc43a/tenor.gif?itemid=12502580"
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
    async def add_meme(self, ctx, link_to_meme, *, meme_name):
        meme_name = meme_name.lower()
        # If the user tries to overwrite the list of memes, they are prevented..
        if meme_name == "help":
            await ctx.send(
                "You cannot override the list of all the memes, you storming fool!"
            )
            return
        # Add meme to database.
        memes_collection = get_collection("memes")
        insert_meme(memes_collection, meme_name, link_to_meme)
        await ctx.send("The meme has been added.")

    @commands.command(
        aliases=["delmeme"], brief="Removes the meme from the meme database"
    )
    @commands.is_owner()
    async def delete_meme(self, ctx, *, meme_name):
        meme_name = meme_name.lower()
        memes_collection = get_collection("memes")
        meme = get_meme(memes_collection, meme_name)
        if meme is not None:
            delete_meme(memes_collection, meme["_id"])
            await ctx.send("The meme has been removed.")
        else:
            await ctx.send("No such meme exists. You messed up!")

    @commands.command(
        aliases=["change_meme_description", "changedes"],
        brief="Changes meme description",
    )
    @commands.has_permissions(administrator=True)
    async def set_meme_description(self, ctx, meme_name, *, description):
        meme_name = meme_name.lower()
        meme_name = meme_name.replace("-", " ")
        meme_name = meme_name.replace("_", " ")

        memes_collection = get_collection("memes")
        meme = get_meme(memes_collection, meme_name)
        if meme is not None:
            update_meme(memes_collection, meme["_id"], "description", description)
            await ctx.send(
                f"The description of | **{meme_name}** | "
                "has been changed to _'{description}'_."
            )
        else:
            await ctx.send("No such meme exists. You messed up!")

    @commands.command(
        aliases=["printapi"],
        brief="Print number of API requests",
        description="Print number of Google API requests. "
        "Tracked while executing places search.",
    )
    @commands.is_owner()
    async def print_api(self, ctx, api_provider):
        try:
            apis_collection = get_collection("apis")
            api = get_api(apis_collection, api_provider)
            requests_count = api["number_of_calls"]
            await ctx.send(
                f"Current number of {api_provider} "
                f"API requests executed: **{requests_count}**"
            )
        except TypeError:
            await ctx.send("Such API provider isn't registered in the database.")

    @commands.command(
        aliases=["resetapi"],
        brief="Reset tracked number of API requests",
        description="Reset tracked number of Google API requests. "
        "Tracked while executing places search.",
    )
    @commands.is_owner()
    async def reset_api(self, ctx, api_provider):
        try:
            apis_collection = get_collection("apis")
            reset_api(apis_collection, api_provider)
            await ctx.send(
                f"Number of {api_provider} API requests successfully reset to 0."
            )
        except TypeError:
            await ctx.send("Such API provider isn't registered in the database.")


async def setup(client):
    await client.add_cog(Mod(client))
