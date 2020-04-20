from discord.ext import commands
from cogs.config import config

bot = commands.Bot(command_prefix='!')
bot.load_extension('cogs.maincog')
bot.load_extension('cogs.servercog')
bot.run(config['token'])