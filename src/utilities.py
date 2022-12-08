import os
import random
import zipfile
from dateutil import parser
from bson.objectid import ObjectId

import pymongo

from main import MONGODB_CONNECTION_STRING

# Discord message length limit.
MESSAGE_CHARACTER_LIMIT = 2000


# Simple exception for raising when input is too heavy to handle by the bot.
class RoughInputException(Exception):
    pass


def get_collection(collection_name: str) -> pymongo.collection.Collection:
    """Get specified collection from the Pomelo Database."""
    mongo_client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
    pomelo_db = mongo_client["pomelo_db"]
    return pomelo_db[collection_name]


# APIs functions
def get_api(apis_collection: pymongo.collection.Collection, api_provider: str) -> dict:
    api = apis_collection.find_one({"provider": api_provider})
    return api


def update_api(
    apis_collection: pymongo.collection.Collection,
    api_provider: str,
    number_of_calls: int,
):
    apis_collection.update_one(
        {"provider": api_provider}, {"$set": {"number_of_calls": number_of_calls}}
    )


def reset_api(apis_collection: pymongo.collection.Collection, api_provider: str):
    apis_collection.update_one(
        {"provider": api_provider}, {"$set": {"number_of_calls": 0}}
    )


# To-do functions
def insert_todo(
    todos_collection: pymongo.collection.Collection, timestamp: str, todo_content: str
):
    # Convert date string to Date object.
    timestamp = parser.parse(timestamp)
    todo = {"timestamp": timestamp, "content": todo_content}
    todos_collection.insert_one(todo)


def delete_todo(todos_collection: pymongo.collection.Collection, todo_id):
    todos_collection.delete_one({"_id": ObjectId(todo_id)})


def get_todos_as_entries(todos_collection) -> list:
    """Get all the todos from the database and return it as a printable list of entries."""
    todos = todos_collection.find().sort("timestamp")
    todo_list = []
    for item in todos:
        todo_id = item["_id"]
        timestamp = item["timestamp"]
        content = item["content"]
        meme_entry = f"- ID: {todo_id} - {timestamp} | {content}"
        todo_list.append(meme_entry)

    return todo_list


# Memes functions
def get_all_memes(memes_collection: pymongo.collection.Collection) -> list:
    """Index all the memes from the shelve database and display a list of memes to the user."""
    memes = memes_collection.find()
    return memes


def get_meme(memes_collection: pymongo.collection.Collection, meme_name: str) -> dict:
    """Get single meme based on its name."""
    meme = memes_collection.find_one({"name": meme_name})
    return meme


def update_meme(
    memes_collection: pymongo.collection.Collection, meme_id, attribute: str, value
):
    memes_collection.update_one({"_id": meme_id}, {"$set": {attribute: value}})


def delete_meme(memes_collection: pymongo.collection.Collection, meme_id):
    memes_collection.delete_one({"_id": meme_id})


def insert_meme(
    memes_collection: pymongo.collection.Collection,
    meme_name: str,
    meme_url: str,
    meme_description: str = "*new meme*",
):
    meme = {
        "name": meme_name,
        "description": meme_description,
        "times_used": 0,
        "url": meme_url,
    }
    memes_collection.insert_one(meme)


def get_memes_as_entries(memes_collection: pymongo.collection.Collection) -> list:
    """Get all the memes from the database and return it as a printable list of entries."""
    memes = memes_collection.find().sort("name")
    memes_list = []
    for item in memes:
        name = item["name"]
        description = item["description"]
        times_used = item["times_used"]
        meme_entry = f"- {name} | {description} | times used: {times_used}"
        memes_list.append(meme_entry)

    return memes_list


async def send_with_buffer(
    ctx, message_entries: list, separator="\n", message_block_indicator="```"
):
    """Send data using multiple messages to work around Discord's character limit."""
    buffer = ""
    for index, entry in enumerate(message_entries):
        # Ensure 'entry' is a string so it can be concatenated.
        entry = str(entry)
        # When the buffer exceeds max character limit, dump the contents of the buffer into the message.
        if (
            len(
                message_block_indicator
                + buffer
                + entry
                + separator
                + message_block_indicator
            )
            >= MESSAGE_CHARACTER_LIMIT
        ):
            await ctx.send(message_block_indicator + buffer + message_block_indicator)
            buffer = ""

        buffer = buffer + entry
        if index != len(message_entries) - 1:
            buffer += separator

    await ctx.send(message_block_indicator + buffer + message_block_indicator)


async def handle_dice_roll(dice_roll: str, ctx) -> tuple:
    """Handle a single dice roll provided in format: <number_of_dices>d<sides_of_dice>,
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
            if (
                filename == zip_filename
            ):  # Can change it so for example,it only backs up .py files.
                continue  # don"t backup the backup ZIP files

            backup_zip.write(os.path.join(foldername, filename))
    backup_zip.close()
    print("The backup has been completed.")
