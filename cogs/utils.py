import shelve
import plotly.graph_objects as go
import plotly.offline
import random as rand
import psutil

from datetime import datetime
from discord.ext import commands

MSG_CHAR_LIMIT = 2000  # Max message length on Discord.


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
        with open('data/todo_list.txt', 'a') as todo_file:
            todo_string = '# TODO: ' + todo_content + ' - ' + str(datetime.now().strftime('%Y-%m-%d %H:%M')) + '\n'
            todo_file.write(todo_string)

            await ctx.send('The TODO has been added.')

    @commands.command(aliases=['todolist'],
                      description='Shows the TODO list. I mean, if we have the list already might as well take a look '
                                  'at it...')
    async def todo_list(self, ctx):
        with open('data/todo_list.txt', 'r') as todo_file:
            buffer = ''
            for line in todo_file.readlines():

                # When the buffer overloads (i.e. exceeds 2 000 character limit),
                # dump the contents of the buffer into the message.
                if len('```' + buffer + line + '\n```') >= MSG_CHAR_LIMIT:
                    await ctx.send('```' + buffer + '```')
                    buffer = ''

                buffer = buffer + line + '\n'

            await ctx.send('```' + buffer + '```')

    @commands.command(aliases=['deltodo'])
    @commands.has_permissions(administrator=True)
    async def del_todo(self, ctx, line_index):
        try:
            line_index = int(line_index)
        except ValueError:
            line_index = -1  # Returns negative line index to indicate an error has occured.

        if line_index >= 0:
            with open('data/todo_list.txt', 'r') as todo_file:
                todoes = todo_file.readlines()
                await ctx.send('Deleting line # ' + str(line_index) +
                               '\nHere\'s its content:\n```' + todoes[line_index] + '```')
                del todoes[line_index]
            with open('data/todo_list.txt', 'w') as todo_file:
                todo_file.writelines(todoes)
            await ctx.send('The TODO has been deleted.')

        else:
            await ctx.send('Yoo, mate! That ain\'t really a well-suited number, ya know?')

    @commands.command(aliases=['memedata'])
    async def meme_data(self, ctx, *, keyword):
        with shelve.open('data/memes_shelf') as memes_shelf:
            meme_content = memes_shelf[keyword]
            await ctx.send(str(meme_content))

    @commands.command(aliases=['plotmemes'])
    async def plot_memes(self, ctx):
        # TODO: Work on it
        x_axis = ['one', 'two', 'three', 'four', 'five',
                  'six', 'seven', 'eight', 'nine', 'ten']
        y_axis = rand.sample(range(50), 10)

        fig = go.Figure([go.Bar(x=x_axis, y=y_axis)])
        fig.update_layout(barmode='group', xaxis_tickangle=-45)
        fig.show()
        # fig.write_image('data/meme_plot.jpeg')

        # await ctx.send(file=open('data/meme_plot.jpeg'))


def setup(client):
    client.add_cog(Utils(client))
