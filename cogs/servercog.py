from datetime import datetime

from discord.ext import commands

from .ripserver import RipServer
from config import config

class ServerCog(commands.Cog):

    TEAM_TRANSLATION = {
        1: "left side faction",
        2: "right side faction",
        0: "unassigned"
    }


    def __init__(self, bot):
        self.bot = bot
        self.config = config
        self.auth_token = config['token']
        self.rip_server = RipServer(self.config)

    @commands.command(name='ripbalance')
    async def ripbalance(self, ctx):
        """Reports the current balance of RIP players per team"""
        team_balances = self.rip_server.rip_balance()

        balance_left = team_balances.get(1, 0)
        balance_right = team_balances.get(2, 0)
        balance_difference = abs(balance_left - balance_right)

        msg = "RIP BALANCE: {0} -vs- {1} \n".format(balance_left, balance_right)
        if balance_difference <= 3:
            msg += "*Server is balanced (3 or less difference)*"
        elif balance_left > balance_right:
            msg += "*RIP Imbalance! Please join the faction on the right to ensure RIP members are balanced.*"
        elif balance_right > balance_left:
            msg += "*RIP Imbalance! Please join the faction on the left on the to ensure RIP members are balanced.*"
        else:
            msg += "*Feel free to join either side.*"

        await ctx.channel.send(msg)

    @commands.command(name='online')
    async def online(self, ctx):
        """Reports which RIP players are on each team, including join time"""
        teams = self.rip_server.get_teams_rip_only()
        sessions = self.rip_server.get_sessions(self.config['battlemetrics']['server'])

        if not teams:
            await ctx.channel.send("Server empty.")
            return

        msg = "RIP Members online (with join time):\n"
        for team_id in sorted(teams.keys()):
            msg += "{0}\n".format(self.TEAM_TRANSLATION[team_id])

            players_unsorted = teams[team_id]
            players_sorted = sorted(players_unsorted, key= lambda x: sessions[x.attributes.id])

            if len(players_sorted) == 0:
                msg += "- No RIP on this side"

            for player in players_sorted:
                player_name = player.attributes.name
                session_raw = sessions[player.attributes.id]
                session_datetime = datetime.strptime(session_raw, "%Y-%m-%dT%H:%M:%S.%fZ")

                msg  += "- {0} ({1})\n".format(
                    player_name,
                    session_datetime.strftime("%H:%M:%S"))
            msg += "\n"
        
        await ctx.channel.send(msg)

 
def setup(bot):
    bot.add_cog(ServerCog(bot))



