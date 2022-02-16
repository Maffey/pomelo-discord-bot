import random
import re
import requests
import bs4
import pyinputplus as pyip

from discord.ext import commands, tasks

from src.main import POMELO_CLIENT
from src.utilities import (
    RoughInputException,
    send_with_buffer,
    MESSAGE_CHARACTER_LIMIT,
    handle_dice_roll,
    get_memes_as_entries,
    get_meme,
    get_collection,
    update_meme,
)


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
            update_meme(
                memes_collection, meme["_id"], "times_used", meme["times_used"] + 1
            )
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

    @commands.command(
        brief="Check status of the given server",
        description="Based on the server name provided, check the official website for server status.",
    )
    async def status(self, ctx, target_server: str = "Bran"):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0"
        }
        response = requests.get(
            "https://www.newworld.com/en-us/support/server-status", headers=headers
        )
        response.raise_for_status()
        soup = bs4.BeautifulSoup(response.text, "html.parser")

        # Find all entries for all servers
        server_elements = soup.find_all(
            "div", {"class": "ags-ServerStatus-content-responses-response-server"}
        )
        for server in server_elements:
            server_name_element = server.find(
                "div",
                {"class": "ags-ServerStatus-content-responses-response-server-name"},
            )
            server_name = server_name_element.text.strip()
            if server_name == target_server:
                # If name is the same as searched one, get the status.
                server_wrapper_element = server.find(
                    "div",
                    {
                        "class": "ags-ServerStatus-content-responses-response-server-status-wrapper"
                    },
                )
                server_status_element = server_wrapper_element.find("div")
                server_status = server_status_element["title"]
                await ctx.send(f"Server {server_name} status: **{server_status}**")

    @commands.command(
        aliases=["mhproblem", "mhp", "montyhallproblem"],
        brief="Play the game that demonstrates the Monty Hall problem",
        description="Play the game that demonstrates the Monty Hall problem, where you pick doors and win prizes!",
    )
    async def monty_hall_problem(self, ctx):
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        prize_name = "CAR"
        non_prize_name = "GOAT"
        game_view_template = "[1] [2] [3]"

        game_view = game_view_template
        possible_rewards = [non_prize_name, non_prize_name, prize_name]
        # Randomize rewards order
        random.shuffle(possible_rewards)
        # Assign rewards to a dictionary where number is the key.
        rewards_behind_doors = {
            doors_index + 1: reward
            for (doors_index, reward) in enumerate(possible_rewards)
        }

        await ctx.send(
            "There are three doors. Behind two of them is just a goat. "
            "But one of the doors hides the prize of this contest: a brand new car!\n"
            "Which doors will you pick?\n"
            f"{game_view}"
        )
        while True:
            try:
                user_selected_door_index = int(
                    (
                        await self.client.wait_for("message", check=check, timeout=30)
                    ).content
                )
                if user_selected_door_index < 1 or user_selected_door_index > 3:
                    raise KeyError
                else:
                    break
            except ValueError:
                await ctx.send(f"{ctx.message.author.mention} This is not a number.")
            except KeyError:
                await ctx.send(
                    f"{ctx.message.author.mention} Number must be between 1 and 3."
                )

        doors_available_to_reveal = {
            doors_index: reward
            for (doors_index, reward) in rewards_behind_doors.items()
            if reward != prize_name and doors_index != user_selected_door_index
        }
        revealed_doors_index = random.choice(list(doors_available_to_reveal))

        game_view = game_view.replace(str(revealed_doors_index), non_prize_name)
        game_view = game_view.replace(
            str(user_selected_door_index), f"**{user_selected_door_index}**"
        )

        await ctx.send(
            f"You have selected door number [{user_selected_door_index}].\n"
            f"I will now reveal to you what's behind one of the other doors. "
            f"Behind doors number [{revealed_doors_index}] there's a goat.\n"
            f"This means, your current situation in the game looks like this:\n"
            f"{game_view}\n"
            f"I marked your choice in bold.\n"
            f"Now, here's the trick: you are allowed to change door you have selected to the unrevealed "
            f"one, if you want.\n "
            f"You don't have to, of course. So, are we changing the doors? [y/N]"
        )

        does_user_change_doors = (
            await self.client.wait_for("message", check=check, timeout=30)
        ).content
        message_selection_change: str
        if does_user_change_doors == "y":
            # TODO There's got to be a more readable way for that.
            user_selected_door_index = [
                doors_index
                for doors_index in rewards_behind_doors.keys()
                if doors_index != user_selected_door_index
                and doors_index != revealed_doors_index
            ][0]
            message_selection_change = (
                f"Changing the selected doors to number [{user_selected_door_index}]. "
                f"Good call!"
            )
        else:
            message_selection_change = "You haven't changed your pick.\n"

        message_game_result: str
        if rewards_behind_doors[user_selected_door_index] == prize_name:
            message_game_result = f"Congratulations! Your reward is a brand new CAR!"
        else:
            message_game_result = (
                f"Unfortunately you have lost. Your reward is a GOAT :("
            )

        game_view = game_view_template
        for door_index, reward in rewards_behind_doors.items():
            game_view = game_view.replace(str(door_index), f"{door_index}={reward}")

        await ctx.send(
            f"{message_selection_change}\n{message_game_result}\nHere's what the doors have been hiding from the beginning:\n"
            f"{game_view}\nIf you have decided to change the doors, even if you have lost - you actually made the correct choice.\n"
            f"Yes, it might seem weird, but when you change the doors, you actually increase your chance to win.\n"
            f"It might seem unintuitive, but math is on your side!\n"
            f"To see more, check out Wikipedia: https://en.wikipedia.org/wiki/Monty_Hall_problem"
        )

    @tasks.loop(hours=24)
    async def change_administrator(self, ctx):
        # Getting the roles that have administrator set to True
        admin_roles = [
            role
            for role in ctx.guild.roles
            if role.permissions.administrator and role.name not in ["Pancake", "Pomelo"]
        ]

        await ctx.send(admin_roles)

    @commands.command(
        aliases=["startmadness"],
        brief="Let the chaos begin.",
        description="Let the chaos begin. Do not use at home.",
    )
    async def start_madness(self, ctx):
        self.change_administrator.start(ctx)


def setup(client):
    client.add_cog(Fun(client))
