import shelve
from datetime import datetime

from discord.ext import commands


class Utils(commands.Cog):

    def __init__(self, client):
        self.client = client

        # Checks how much delay is there between bot and the server.

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.client.latency * 1000)} ms')

    @commands.command(aliases=['addtodo'],
                      description='Adds a TODO to the list of things that will probably never be done. I hate myself. '
                                  'Life is suffering. The endless oblivion of things that should be done will '
                                  'eventually catch up with us all, causing devastation, chaos and misery. You really '
                                  'want to contribute to it? That "one additional thing we have to do" which you will '
                                  'NEVER do? Think twice before adding anything, please.')
    @commands.has_permissions(administrator=True)
    async def add_todo(self, ctx, *, todo_content):
        # Adds a line to todo_list.txt in following format:
        # <todo content> - <date>
        todo_file = open('/home/ubuntu/PomeloDiscordBot/data/todo_list.txt', 'a')
        todo_string = '# TODO: ' + todo_content + ' - ' + str(datetime.now().strftime('%Y-%m-%d %H:%M')) + '\n'
        todo_file.write(todo_string)
        await ctx.send('The TODO has been added.')
        todo_file.close()

    @commands.command(aliases=['todolist'],
                      description='Shows the TODO list. I mean, if we have the list already might as well take a look '
                                  'at it...')
    async def todo_list(self, ctx):
        todo_file = open('/home/ubuntu/PomeloDiscordBot/data/todo_list.txt', 'r')
        await ctx.send(todo_file.read())

    @commands.command(aliases=['showmemedata'])
    async def show_meme_data(self, ctx, *, keyword):
        with shelve.open('/home/ubuntu/PomeloDiscordBot/data/memes_shelf') as memes_shelf:
            meme_content = memes_shelf[keyword]
            await ctx.send(str(meme_content))


def setup(client):
    client.add_cog(Utils(client))
