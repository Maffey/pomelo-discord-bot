import random
import shelve

from discord.ext import commands

MSG_CHAR_LIMIT = 2000  # Max message length on Discord.


class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client


    '''
    Chooses a random response from the ones below to respond to user's question.
    '''

    @commands.command(aliases=['8ball'], description='Standard 8ball game.')
    async def _8ball(self, ctx, *, question):
        responses = ['It is certain.',
                     'It is decidedly so.',
                     'Without a doubt.',
                     'Yes - definitely.',
                     'You may rely on it.',
                     'As I see it, yes.',
                     'Most likely.',
                     'Outlook good.',
                     'Yes.',
                     'Signs point to yes.',
                     'Reply hazy, try again.',
                     'Ask again later.',
                     'Better not tell you now.',
                     'Cannot predict now.',
                     'Concentrate and ask again.',
                     'Don\'t count on it.',
                     'My reply is no.',
                     'My sources say no.',
                     'Outlook not so good.',
                     'Very doubtful.',
                     '¯\\_(ツ)_/¯']

        await ctx.send(f'Question was: {question}\nAnswer: {random.choice(responses)}')

    '''
    Sends the meme an user wants to be sent by pasting a hyperlink from PostImage library.
    '''

    @commands.command(description='Send a desired meme to the chat. Type "help" to get a list of all memes.')
    async def meme(self, ctx, *, keyword):

        # TODO: Add bufer to a function in another, helper file (together with max_msg_length) and use it from there.
        keyword = keyword.lower()
        if keyword == 'help':
            help_content = display_meme_help()

            buffer = ''
            for meme in help_content:

                # When the buffer overloads (i.e. exceeds 2 000 character limit),
                # dump the contents of the buffer into the message.
                if len('```' + buffer + meme + '\n```') >= MSG_CHAR_LIMIT:
                    await ctx.send('```' + buffer + '```')
                    buffer = ''

                buffer = buffer + meme + '\n'

            await ctx.send('```' + buffer + '```')
            return

        with shelve.open('data/memes_shelf') as memes_shelf:

            try:
                # Sends link to a meme which is saved inside the shelf.
                await ctx.send(memes_shelf[keyword]['hyperlink'])
            except KeyError:
                await ctx.send('No such meme exists. You messed up!')

            # Stores the frequency of usage.
            new_freq = memes_shelf[keyword]['frequency'] + 1
            memes_shelf[keyword] = {'hyperlink': memes_shelf[keyword]['hyperlink'],
                                    'description': memes_shelf[keyword]['description'], 'frequency': new_freq}

    @commands.command(aliases=['mammamia', 'mamma-mia'], description='Japierdole, Karolina!')
    async def mamma_mia(self, ctx):
        karolina_sounds = ('https://vocaroo.com/i/s1ky8bx7G2iR', 'https://vocaroo.com/i/s0dPvj6JAh8b',
                           'https://vocaroo.com/i/s19RlC11goAh')
        await ctx.send(f'https://i.imgflip.com/noa52.jpg\n{random.choice(karolina_sounds)}')

    @commands.command(aliases=['stopmati', 'stop-mati'], description='Nie no mati kurwa nie swiruj')
    async def stop_mati(self, ctx):
        await ctx.send('https://i.postimg.cc/nr7rkLPJ/stop-mati.jpg')

    @commands.command(aliases=['..'])
    async def dot(self, ctx):
        await ctx.send('Why you trippin\' bruh?')


def display_meme_help():
    memes_list = []
    with shelve.open('data/memes_shelf') as memes_shelf:
        meme_keys = list(memes_shelf.keys())
        for key in meme_keys:
            description = memes_shelf[key]['description']
            meme_entry = f'* | {key} | - {description}'
            memes_list.append(meme_entry)

    return memes_list


def setup(client):
    client.add_cog(Fun(client))
