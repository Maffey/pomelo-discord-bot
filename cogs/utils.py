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
        with open('/home/ubuntu/PomeloDiscordBot/data/todo_list.txt', 'a') as todo_file:
            todo_string = '# TODO: ' + todo_content + ' - ' + str(datetime.now().strftime('%Y-%m-%d %H:%M')) + '\n'
            todo_file.write(todo_string)

            await ctx.send('The TODO has been added.')

    @commands.command(aliases=['todolist'],
                      description='Shows the TODO list. I mean, if we have the list already might as well take a look '
                                  'at it...')
    async def todo_list(self, ctx):
        with open('/home/ubuntu/PomeloDiscordBot/data/todo_list.txt', 'r') as todo_file:
            await ctx.send(todo_file.read())

    @commands.command(aliases=['deltodo'])
    @commands.has_permissions(administrator=True)
    async def del_todo(self, ctx, line_index):
        if line_index >= 0:
            with open('/home/ubuntu/PomeloDiscordBot/data/todo_list.txt', 'r') as todo_file:
                todoes = todo_file.readlines()
                await ctx.send('DEBUG: Deleting line no. ' + str(line_index) +
                               '\nHere is its content: ' + todoes[line_index])
                del todoes[line_index]
            with open('/home/ubuntu/PomeloDiscordBot/data/todo_list.txt', 'w') as todo_file:
                await ctx.send('DEBUG: Writing todo_file:' + '\n'.join(todoes))
                todo_file.writelines(todoes)
            await ctx.send('The TODO has been deleted.')

        else:
            await ctx.send('That\'s not a correct line number, mate!')

    @commands.command(aliases=['memedata'])
    async def meme_data(self, ctx, *, keyword):
        with shelve.open('/home/ubuntu/PomeloDiscordBot/data/memes_shelf') as memes_shelf:
            meme_content = memes_shelf[keyword]
            await ctx.send(str(meme_content))

    @commands.command(aliases=['plotmemes'])
    async def plot_memes(self, ctx):
        await ctx.send('There should be a plotly graph displayed. But I\'m lazy. Give me a break.')


def setup(client):
    client.add_cog(Utils(client))
