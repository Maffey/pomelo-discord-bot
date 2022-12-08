import time
from datetime import datetime

import discord.file
import googlemaps
import matplotlib.pyplot as plt
import pandas as pd
import psutil
from bson.errors import InvalidId
from discord.ext import commands

from main import GOOGLE_API_TOKEN, REQUESTS_COUNTER_FILE
from utilities import (
    send_with_buffer,
    backup_to_zip,
    get_collection,
    get_meme,
    get_all_memes,
    insert_todo,
    delete_todo,
    get_todos_as_entries,
    get_api,
    update_api,
)


class Utils(commands.Cog):
    def __init__(self, client):
        self.client = client

        # Checks how much delay is there between bot and the server.

    @commands.command(brief="Pings bot to check latency")
    async def ping(self, ctx):
        await ctx.send(f"Pong! {round(self.client.latency * 1000)} ms")

    @commands.command(
        aliases=["addtodo"],
        brief="Adds a TODO entry to the TODO list",
        description="Adds a TODO to the list of things that will probably never be done. I hate myself. "
        "Life is suffering. The endless oblivion of things that should be done will "
        "eventually catch up with us all, causing devastation, chaos and misery. You really "
        "want to contribute to it? That 'one additional thing we have to do' which you will "
        "NEVER do? Think twice before adding anything, please.",
    )
    @commands.is_owner()
    async def add_todo(self, ctx, *, todo_content):
        todos_collection = get_collection("todos")
        timestamp = str(datetime.now())
        insert_todo(todos_collection, timestamp, todo_content)

        await ctx.send("The TODO has been added.")

    @commands.command(
        aliases=["todolist"],
        brief="Shows the TODO list",
        description="Shows the TODO list. I mean, if we have the list already, might as well take a look "
        "at it...",
    )
    async def todo_list(self, ctx):
        todos_collection = get_collection("todos")
        todos = get_todos_as_entries(todos_collection)
        await send_with_buffer(ctx, todos)

    @commands.command(
        aliases=["deltodo"],
        brief="Removes a TODO entry",
        description="Removes given TODO entry from the list of TODO entries by the selected ID. "
        "Copy the ID from the displayed list (.todo_list command)",
    )
    @commands.is_owner()
    async def del_todo(self, ctx, todo_id):
        try:
            todos_collection = get_collection("todos")
            delete_todo(todos_collection, todo_id)
            await ctx.send("The TODO has been deleted.")
        except InvalidId:
            await ctx.send("TODO with such ID simply doesn't exist.")

    @commands.command(
        aliases=["memedata"],
        brief="Shows dictionary data about a meme",
        description="Shows dictionary data about a meme, taken directly from the meme database, "
        "such as the direct link to the image, "
        "description or how many times the meme was used.",
    )
    async def meme_data(self, ctx, *, meme_name):
        memes_collection = get_collection("memes")
        meme = get_meme(memes_collection, meme_name)
        if meme is not None:
            await ctx.send(meme)
        else:
            await ctx.send("No such meme exists. You messed up!")

    @commands.command(
        aliases=["plotmemes", "pltm"],
        brief="Plots how often memes are used",
        description="Plots how many times memes have been used using matplotlib and "
        "sends the image of the graph as a file.",
    )
    async def plot_memes(self, ctx, times_used_limit=0):

        memes_collection = get_collection("memes")
        memes_list = get_all_memes(memes_collection)
        memes_to_plot = []
        for meme_document in memes_list:
            times_used = meme_document["times_used"]
            if times_used > times_used_limit:
                name = meme_document["name"]
                memes_to_plot.append((name, times_used))

        # Sort the memes by frequency and capture their names and values into lists
        memes_to_plot = sorted(memes_to_plot, key=lambda meme: meme[1], reverse=True)
        meme_names = [meme[0] for meme in memes_to_plot]
        meme_frequencies = [meme[1] for meme in memes_to_plot]

        # Plot the memes on the graph.
        plt.bar(meme_names, meme_frequencies)
        plt.title("Usage of memes")
        plt.xticks(rotation=90)
        plt.xlabel("Meme names")
        plt.ylabel("Times used")
        plt.savefig("data/memes_chart.png", bbox_inches="tight")
        plt.close()
        await ctx.send(
            "Here's your graph. Enjoy!", file=discord.File("data/memes_chart.png")
        )

    @commands.command(
        brief="Creates a backup of 'data' directory",
        description="Creates a backup of 'data' directory which contains mutable data such as "
        "meme database, TODO list, etc..",
    )
    @commands.is_owner()
    async def backup(self, ctx):
        backup_to_zip()
        await ctx.send("The backup has been completed.")

    @commands.command(
        brief="Get system metrics",
        description="Get data about system metrics such as CPU and memory usage.",
    )
    async def stats(self, ctx):
        await ctx.send("Gathering data, please wait...")
        cpu_load = psutil.cpu_percent(4)
        memory_usage = psutil.virtual_memory()[2]

        await ctx.send(
            " ===== **SYSTEM METRICS** ===== \n"
            f"**CPU Load:** \t{cpu_load} %\n"
            f"**RAM Load:**\t{memory_usage} %\n"
        )

    @commands.command(
        aliases=["sp"],
        brief="Search nearby places",
        description="Search nearby places using Google Maps API. Requires search query, city and distance in km.",
    )
    async def search_places(self, ctx, searched_place, city, distance=10):
        await ctx.send(
            f"Searching for {searched_place} in {city}, radius: {distance}..."
        )
        api_provider = "Google"
        # Setup Google Maps API client.
        map_client = googlemaps.Client(GOOGLE_API_TOKEN)
        # Find location data based on search query - in this case: city.
        geocode_result = map_client.geocode(city)
        # Extract latitude and longitude from geocode result.
        coordinates = geocode_result[0]["geometry"]["location"]
        location = (coordinates["lat"], coordinates["lng"])
        # With this variable, track found places.
        places_list = []
        # Convert kilometers to meters
        distance = distance * 1000

        # Read current number of API requests already executed into variable.
        apis_collection = get_collection("apis")
        api = get_api(apis_collection, api_provider)
        requests_count = api["number_of_calls"]

        # Perform the search.
        response = map_client.places_nearby(
            location=location, keyword=searched_place, radius=distance
        )
        # Count the number of requests.
        requests_count += 1

        places_list += response.get("results")
        # This token is neeeded to track our position on the search list.
        # Google Maps allows for max. 20 results on one page.
        next_page_token = response.get("next_page_token")

        # Call API for more places results as long as there are any.
        while next_page_token:
            time.sleep(2)
            response = map_client.places_nearby(
                location=location,
                keyword=searched_place,
                radius=distance,
                page_token=next_page_token,
            )
            requests_count += 1
            places_list += response.get("results")
            next_page_token = response.get("next_page_token")

        # Update document in database.
        update_api(apis_collection, api_provider, requests_count)

        df = pd.DataFrame(places_list)
        # Store Google Maps url with the given place.
        df["url"] = "www.google.com/maps/place/?q=place_id:" + df["place_id"]
        # Remove closed locations.
        df.drop(df[df.business_status != "OPERATIONAL"].index, inplace=True)
        # Remove low rating locations.
        df.drop(df[df.rating <= 3.5].index, inplace=True)

        # Reduce data frame to the most important columns.
        df = df[["name", "rating", "vicinity", "url"]]
        df_rows = df.to_string(index=False).split(sep="\n")
        await send_with_buffer(ctx, df_rows, separator="\n\n")


async def setup(client):
    await client.add_cog(Utils(client))
