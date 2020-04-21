from discord.ext import commands
from cogs.config import config

if config.get('bugsnag_token'):
    import bugsnag
    import logging
    from bugsnag.handlers import BugsnagHandler

    bugsnag.configure(
        api_key=config['bugsnag_token'],
        project_root="/path/to/your/app",
    )
    logger = logging.getLogger("test.logger")
    handler = BugsnagHandler()
    # send only ERROR-level logs and above
    handler.setLevel(logging.ERROR)
    logger.addHandler(handler)
    print("Bugsnag Crash reporting active.")

bot = commands.Bot(command_prefix='!')
bot.load_extension('cogs.maincog')
bot.load_extension('cogs.servercog')
bot.run(config['token'])
