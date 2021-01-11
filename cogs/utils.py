import os
import shelve
import zipfile
import discord.file
import matplotlib.pyplot as plt
from discord.ext import commands
from datetime import datetime
from main import MSG_CHAR_LIMIT


def backup_to_zip():
    # Backup the entire contents of "data" folder into a ZIP file.
    folder = "data"

    folder = os.path.abspath(folder)  # make sure folder is absolute

    # Figure out the filename this code should use based on what files already exist.
    zip_filename = os.path.basename(folder) + "_backup.zip"

    # Create the ZIP file.
    print(f"Creating {zip_filename}")
    backup_zip = zipfile.ZipFile(zip_filename, "w")

    # Walk the entire folder tree and compress the files in each folder.
    for foldername, subfolders, filenames in os.walk(folder):
        print(f"Adding files in {foldername} to backup...")
        # Add the current folder to the ZIP file.
        backup_zip.write(foldername)
        # Add all the files in this folder to the ZIP file.
        for filename in filenames:
            if filename == zip_filename:  # Can change it so for example,it only backs up .py files.
                continue  # don"t backup the backup ZIP files

            backup_zip.write(os.path.join(foldername, filename))
    backup_zip.close()
    print("The backup has been completed.")


class Utils(commands.Cog):

    def __init__(self, client):
        self.client = client

        # Checks how much delay is there between bot and the server.

    @commands.command(brief="Pings bot to check latency")
    async def ping(self, ctx):
        await ctx.send(f"Pong! {round(self.client.latency * 1000)} ms")

    @commands.command(aliases=["addtodo"],
                      brief="Adds a TODO entry to the TODO list",
                      description="Adds a TODO to the list of things that will probably never be done. I hate myself. "
                                  "Life is suffering. The endless oblivion of things that should be done will "
                                  "eventually catch up with us all, causing devastation, chaos and misery. You really "
                                  "want to contribute to it? That 'one additional thing we have to do' which you will "
                                  "NEVER do? Think twice before adding anything, please.")
    @commands.has_permissions(administrator=True)
    async def add_todo(self, ctx, *, todo_content):
        with open("data/todo_list.txt", "a") as todo_file:
            todo_string = "# TODO: " + todo_content + " - " + str(datetime.now().strftime("%Y-%m-%d %H:%M")) + "\n"
            todo_file.write(todo_string)

            await ctx.send("The TODO has been added.")

    @commands.command(aliases=["todolist"],
                      brief="Shows the TODO list",
                      description="Shows the TODO list. I mean, if we have the list already, might as well take a look "
                                  "at it...")
    async def todo_list(self, ctx):
        with open("data/todo_list.txt", "r") as todo_file:
            buffer = ""
            for line in todo_file.readlines():

                # When the buffer overloads (i.e. exceeds 2 000 character limit),
                # dump the contents of the buffer into the message.
                if len("```" + buffer + line + "\n```") >= MSG_CHAR_LIMIT:
                    await ctx.send("```" + buffer + "```")
                    buffer = ""

                buffer = buffer + line + "\n"

            await ctx.send("```" + buffer + "```")

    @commands.command(aliases=["deltodo"],
                      brief="Removes a TODO entry",
                      description="Removes given TODO entry from the list of TODO entries by the selected index. "
                                  "'0' is the first entry, '1' is the second, etc.")
    @commands.has_permissions(administrator=True)
    async def del_todo(self, ctx, line_index):
        try:
            line_index = int(line_index)
        except ValueError:
            line_index = -1  # Returns negative line index to indicate an error has occured.

        if line_index >= 0:
            with open("data/todo_list.txt", "r") as todo_file:
                todoes = todo_file.readlines()
                await ctx.send("Deleting line # " + str(line_index) +
                               "\nHere's its content:\n```" + todoes[line_index] + "```")
                del todoes[line_index]
            with open("data/todo_list.txt", "w") as todo_file:
                todo_file.writelines(todoes)
            await ctx.send("The TODO has been deleted.")

        else:
            await ctx.send("Yoo, mate! That ain't really a well-suited number, ya know?")

    @commands.command(aliases=["memedata"],
                      brief="Shows dictionary data about a meme",
                      description="Shows dictionary data about a meme, taken directly from the meme database, "
                                  "such as the direct link to the image, "
                                  "description or how many times the meme was used.")
    async def meme_data(self, ctx, *, keyword):
        with shelve.open("data/memes_shelf") as memes_shelf:
            meme_content = memes_shelf[keyword]
            await ctx.send(str(meme_content))

    @commands.command(aliases=["plotmemes", "pltm"],
                      brief="Plots how often memes are used",
                      description="Plots how many times memes have been used using matplotlib and "
                                  "sends the image of the graph as a file.")
    async def plot_memes(self, ctx, limit=0):

        # Get all necessary meme data
        memes = []
        with shelve.open("data/memes_shelf") as memes_shelf:
            meme_keys = list(memes_shelf.keys())
            for key in meme_keys:
                frequency = memes_shelf[key]["frequency"]
                if frequency > limit:
                    memes.append((key, frequency))

        # Sort the memes by frequency and capture their names and values into lists
        memes = sorted(memes, key=lambda meme: meme[1], reverse=True)
        meme_names = [meme[0] for meme in memes]
        meme_frequencies = [meme[1] for meme in memes]

        # Plot it

        plt.bar(meme_names, meme_frequencies)
        plt.title("Usage of memes")
        plt.xticks(rotation=90)
        plt.xlabel("Meme names")
        plt.ylabel("Times used")
        plt.savefig("data/memes_chart.png", bbox_inches="tight")
        plt.close()
        await ctx.send("Here's your graph. Enjoy!", file=discord.File("data/memes_chart.png"))

    @commands.command(brief="Creates a backup of 'data' directory",
                      description="Creates a backup of 'data' directory which contains mutable data such as "
                                  "meme database, TODO list, etc..")
    async def backup(self, ctx):
        backup_to_zip()
        await ctx.send("The backup has been completed.")


def setup(client):
    client.add_cog(Utils(client))
