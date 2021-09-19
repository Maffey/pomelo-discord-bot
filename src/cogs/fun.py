import random
import shelve
import re

from discord.ext import commands

from src.utilities import RoughInputException, send_with_buffer, MESSAGE_CHARACTER_LIMIT, handle_dice_roll,\
    get_memes_as_entries, get_meme, get_collection, update_meme


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["8ball"], brief="Standard 8ball game")
    async def _8ball(self, ctx, *, question):
        """Choose a random response from the ones below to respond to user's question."""
        with open("8ball_responses.txt", "r") as responses_file:
            responses = responses_file.readlines()

        await ctx.send(f"Question was: {question}\nAnswer: {random.choice(responses)}")

    @commands.command(
        brief="Sends a desired meme to the chat",
        description="Sends a desired meme to the chat. Type 'help' to get a list of all memes.",
    )
    async def meme(self, ctx, *, meme_name):
        """Send a meme the user wants to be sent by pasting a hyperlink from shelve database."""
        # Get meme collection
        memes_collection = get_collection("memes")

        meme_name = meme_name.lower()
        if meme_name == "help":
            help_content = get_memes_as_entries(memes_collection)
            await send_with_buffer(ctx, help_content)
            return

        # Get link to a meme which is stored inside the database.
        meme = get_meme(memes_collection, meme_name)
        if meme is not None:
            await ctx.send(meme["url"])
            # Update number of times this meme was used.
            update_meme(memes_collection, meme["_id"], "times_used", meme["times_used"] + 1)
        else:
            await ctx.send("No such meme exists. You messed up!")

    @commands.command(aliases=["mammamia", "mamma-mia"], brief="Japierdole, Karolina!")
    async def mamma_mia(self, ctx):
        karolina_sounds = (
            "https://vocaroo.com/i/s1ky8bx7G2iR",
            "https://vocaroo.com/i/s0dPvj6JAh8b",
            "https://vocaroo.com/i/s19RlC11goAh",
        )
        await ctx.send(
            f"https://i.imgflip.com/noa52.jpg\n{random.choice(karolina_sounds)}"
        )

    @commands.command(aliases=[".."], brief="Don't be salty!")
    async def dot(self, ctx):
        await ctx.send("Why you trippin' bruh?")

    @commands.command(
        aliases=["r"],
        brief="Rolls dice",
        description="Rolls dices based on XdY formula, "
        "where X is a number of dices to be rolled and Y is a number of sides on the dice.",
    )
    async def roll(self, ctx, *, throw_sequence):
        # Define a regex to find all elements and find them.
        elements_regex = r"(\d*d\d+|\d+|[\/\+\-\*])"
        throw_sequence = re.findall(elements_regex, throw_sequence)
        # This collects sequence into printable string to display to the user.
        throw_sequence_print = []
        try:
            # Convert dice rolls to calculated throw values.
            for index, element in enumerate(throw_sequence):
                # If the substring in throw_sequence has a character 'd' in it, that means it's a dice roll.
                if "d" in element:
                    # Handle the dice roll And return the result here.
                    dice_result, dices_list = await handle_dice_roll(element, ctx)
                    # Change the value in the list.
                    throw_sequence[index] = dice_result
                    # Convert dices list into printable string and append it.
                    throw_sequence_print.append(
                        "[ " + " + ".join([f"{dice}" for dice in dices_list]) + " ]"
                    )
                else:
                    # For numbers and operators, simply add it to print sequence.
                    throw_sequence_print.append(element)

            # Join sequence with spaces for readability.
            throw_sequence_print = " ".join(throw_sequence_print)
            # After handling the dices, evaluate the throw_sequence as Python expression to easily calculate result.
            total_result_value = eval("".join(throw_sequence))
            # Store message to send into a variable.
            message_to_send = (
                f"{ctx.message.author.mention} throws: {throw_sequence_print}\n"
                f"**Total: ** {total_result_value}"
            )
            if len(message_to_send) <= MESSAGE_CHARACTER_LIMIT:
                # If message is not too long for Discord systems, send the message.
                await ctx.send(message_to_send)
            else:
                # Otherwise, raise an exception.
                raise RoughInputException

        except (ValueError, SyntaxError):
            await ctx.send(
                "It can't be *that* hard to properly form a dice roll, can it?"
                "Just type sequence of dices, operators and number separated by space, for example: "
                "`5 + 3d8 - 5d6 + 4`. I believe in you."
            )

        except RoughInputException:
            await ctx.send(
                f"{ctx.message.author.mention} Oi! Mate, those numbers of yours - they are way too much!"
                f"Keep it simple!"
            )

    @commands.command(
        brief="Chooses one user from given users",
        description="Chooses one user and mentions them from the list of users provided in the command, "
        "separated by spaces.",
    )
    async def choose(self, ctx, *, list_of_users):
        list_of_users = list_of_users.split()
        await ctx.send(random.choice(list_of_users))


def setup(client):
    client.add_cog(Fun(client))
