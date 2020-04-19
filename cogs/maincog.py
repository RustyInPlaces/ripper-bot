from discord.ext import commands

class MainCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Logged on as {0}'.format(self.bot.user))

def setup(bot):
    bot.add_cog(MainCog(bot))



