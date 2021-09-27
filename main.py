from os import getenv
from dotenv import load_dotenv

from bot import CryptoBot
from discord.ext import commands

load_dotenv()

PREFIX = getenv('PREFIX')
TOKEN = getenv('TOKEN')

bot = commands.Bot(command_prefix=commands.when_mentioned_or(PREFIX),
                   description='Discord crypto bot')

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    print('Logged in as {0} ({0.id})'.format(bot.user))

bot.add_cog(CryptoBot(bot))
bot.run(TOKEN)