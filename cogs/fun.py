import random
import shelve

from discord.ext import commands

from main import send_with_buffer


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

    # TODO: Hide from help?
    @commands.command(aliases=[".."],
                      brief="Don't be salty!")
    async def dot(self, ctx):
        await ctx.send("Why you trippin' bruh?")

    @commands.command(aliases=["r"],
                      brief="Rolls dice",
                      description="Rolls dices based on XdY formula, "
                                  "where X is a number of dices to be rolled and Y is a number of sides on the dice.")
    async def roll(self, ctx, dice_roll):
        try:
            number_of_throws, dice_sides = dice_roll.split("d")
            # If there's no number before 'd', assume only one dice is being thrown.
            if number_of_throws == "":
                number_of_throws = 1
            number_of_throws, dice_sides = int(number_of_throws), int(dice_sides)
            # In case the user wants to throw negative number of dices or make a stupid joke.
            if number_of_throws <= 0 or dice_sides == 69 or dice_sides == 420 or dice_sides == 1337:
                await ctx.send("Ha, ha, so amusing. Someone over here thinks himself a great comedian. "
                               "You really must be fun at parties. Get lost.")
            # If the input is okay and user doesn't try to make stupid jokes, the throws are performed.
            else:
                list_of_throws = [random.randint(1, dice_sides) for _ in range(number_of_throws)]
                # TODO: Mention the user which requested the command.
                await ctx.send(f"Your throws ({number_of_throws}d{dice_sides}):")
                await send_with_buffer(ctx, list_of_throws, " + ")
                # TODO: Optionally, add separators to the number before printing it.
                # https://stackoverflow.com/questions/1823058/how-to-print-number-with-commas-as-thousands-separators
                await ctx.send(f"**Result: {sum(list_of_throws)}**")

        except ValueError:
            await ctx.send("It can't be *that* hard to properly form a dice roll, can it?"
                           "Just type `<dices>d<sides>`. I believe in you.")


def display_meme_help():
    """Index all the memes from the shelve database and display a list of memes to the user."""
    memes_list = []
    with shelve.open("data/memes_shelf") as memes_shelf:
        meme_keys = list(memes_shelf.keys())
        for key in meme_keys:
            description = memes_shelf[key]["description"]
            meme_entry = f"* | {key} | - {description}"
            memes_list.append(meme_entry)

    return memes_list


def setup(client):
    client.add_cog(Fun(client))
