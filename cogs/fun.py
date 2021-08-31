import random
import shelve
import re

from discord.ext import commands

from main import MSG_CHAR_LIMIT, send_with_buffer, RoughInputException


class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["8ball"],
                      brief="Standard 8ball game")
    async def _8ball(self, ctx, *, question):
        """Choose a random response from the ones below to respond to user's question."""
        with open("8ball_responses.txt", "r") as responses_file:
            responses = responses_file.readlines()

        await ctx.send(f"Question was: {question}\nAnswer: {random.choice(responses)}")

    @commands.command(brief="Sends a desired meme to the chat",
                      description="Sends a desired meme to the chat. Type 'help' to get a list of all memes.")
    async def meme(self, ctx, *, keyword):
        """Send a meme the user wants to be sent by pasting a hyperlink from shelve database."""
        keyword = keyword.lower()
        if keyword == "help":
            help_content: list = display_meme_help()
            await send_with_buffer(ctx, help_content)
            return

        with shelve.open("data/memes_shelf") as memes_shelf:
            try:
                # Sends link to a meme which is saved inside the shelf.
                await ctx.send(memes_shelf[keyword]["hyperlink"])
            except KeyError:
                await ctx.send("No such meme exists. You messed up!")

            # Stores the frequency of usage.
            new_freq = memes_shelf[keyword]["frequency"] + 1
            memes_shelf[keyword] = {"hyperlink": memes_shelf[keyword]["hyperlink"],
                                    "description": memes_shelf[keyword]["description"], "frequency": new_freq}

    @commands.command(aliases=["mammamia", "mamma-mia"],
                      brief="Japierdole, Karolina!")
    async def mamma_mia(self, ctx):
        karolina_sounds = ("https://vocaroo.com/i/s1ky8bx7G2iR", "https://vocaroo.com/i/s0dPvj6JAh8b",
                           "https://vocaroo.com/i/s19RlC11goAh")
        await ctx.send(f"https://i.imgflip.com/noa52.jpg\n{random.choice(karolina_sounds)}")

    @commands.command(aliases=[".."],
                      brief="Don't be salty!")
    async def dot(self, ctx):
        await ctx.send("Why you trippin' bruh?")

    @commands.command(aliases=["r"],
                      brief="Rolls dice",
                      description="Rolls dices based on XdY formula, "
                                  "where X is a number of dices to be rolled and Y is a number of sides on the dice.")
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
                    throw_sequence_print.append("[ " + " + ".join([f"{dice}" for dice in dices_list]) + " ]")
                else:
                    # For numbers and operators, simply add it to print sequence.
                    throw_sequence_print.append(element)

            # Join sequence with spaces for readability.
            throw_sequence_print = " ".join(throw_sequence_print)
            # After handling the dices, evaluate the throw_sequence as Python expression to easily calculate result.
            total_result_value = eval("".join(throw_sequence))
            # Store message to send into a variable.
            message_to_send = f"{ctx.message.author.mention} throws: {throw_sequence_print}\n" \
                              f"**Total: ** {total_result_value}"
            if len(message_to_send) <= MSG_CHAR_LIMIT:
                # If message is not too long for Discord systems, send the message.
                await ctx.send(message_to_send)
            else:
                # Otherwise, raise an exception.
                raise RoughInputException

        except (ValueError, SyntaxError):
            await ctx.send("It can't be *that* hard to properly form a dice roll, can it?"
                           "Just type sequence of dices, operators and number separated by space, for example: "
                           "`5 + 3d8 - 5d6 + 4`. I believe in you.")

        except RoughInputException:
            await ctx.send(f"{ctx.message.author.mention} Oi! Mate, those numbers of yours - they are way too much!"
                           f"Keep it simple!")

    @commands.command(brief="Chooses one user from given users",
                      description="Chooses one user and mentions them from the list of users provided in the command, "
                                  "separated by spaces.")
    async def choose(self, ctx, *, list_of_users):
        list_of_users = list_of_users.split()
        await ctx.send(random.choice(list_of_users))


def display_meme_help():
    """Index all the memes from the shelve database and display a list of memes to the user."""
    memes_list = []
    with shelve.open("data/memes_shelf") as memes_shelf:
        meme_keys = list(memes_shelf.keys())
        for key in meme_keys:
            description = memes_shelf[key]["description"]
            meme_entry = f"* | {key} | {description}"
            memes_list.append(meme_entry)

    return memes_list


async def handle_dice_roll(dice_roll: str, ctx) -> tuple:
    """Handle asingle dice roll provided in format: <number_of_dices>d<sides_of_dice>,
    return sum of throws and list of throws."""
    number_of_throws, dice_sides = dice_roll.split("d")
    # If there's no number before 'd', assume only one dice is being thrown.
    if number_of_throws == "":
        number_of_throws = 1
    number_of_throws, dice_sides = int(number_of_throws), int(dice_sides)
    if number_of_throws >= 1000 or dice_sides >= 1000:
        raise RoughInputException
    # In case the user wants to throw negative number of dices.
    if number_of_throws == 0:
        await ctx.send("Yeah. Zero throws. Very funny.")
    else:
        # Calculate the result for throwing dice given amount of times. '_' means the variable is not used.
        dice_throws = [random.randint(1, dice_sides) for _ in range(number_of_throws)]
        return str(sum(dice_throws)), dice_throws


def setup(client):
    client.add_cog(Fun(client))
