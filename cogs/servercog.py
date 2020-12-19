from datetime import datetime, date

from discord.ext import commands, tasks

from .ripserver import RipServer
from cogs.config import config

IMBALANCE_DIFFERENCE_ALLOWED = 3
MAX_IMBALANCE_REMINDERS = 2
WAIT_TIME_BETWEEN_REMINDERS = 5
EARLIEST_ROUND_TIME_FOR_REMINDER = 2
LATEST_ROUND_TIME_FOR_REMINDER = 10

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

        self.previous_map = None
        self.minutes_since_mapchange = 0
        self.reminder_sent_at = -10
        self.reminders_sent = 0


    @commands.command(name='ripbalance')
    async def ripbalance(self, ctx):
        """Reports the current balance of RIP players per team"""
        team_balances = self.rip_server.rip_balance()

        balance_left = team_balances.get(1, 0)
        balance_right = team_balances.get(2, 0)
        balance_difference = abs(balance_left - balance_right)

        msg = "RIP BALANCE: {0} -vs- {1} \n".format(balance_left, balance_right)
        if balance_difference <= IMBALANCE_DIFFERENCE_ALLOWED:
            msg += "*Server is balanced (3 or less difference)*"
        elif balance_left > balance_right:
            msg += "*RIP Imbalance! Please join the faction on the right to ensure RIP members are balanced.*"
        elif balance_right > balance_left:
            msg += "*RIP Imbalance! Please join the faction on the left on the to ensure RIP members are balanced.*"
        else:
            msg += "*Feel free to join either side.*"

        await ctx.author.send(msg)

    @commands.command(name='online')
    async def online(self, ctx=None):
        """Reports which RIP players are on each team, including join time"""
        teams = self.rip_server.get_teams_rip_only()
        sessions = self.rip_server.get_sessions(self.config['battlemetrics']['server'])

        if not teams:
            if ctx:
                await ctx.author.send("Server empty.")
            else:
                await self.rip_squad_channel.send("Server empty.")
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
        
        if ctx:
            await ctx.author.send(msg)
        else:
            await self.rip_squad_channel.send(msg)

    @commands.command(name='update')
    async def update(self, ctx):
        print("Received force refresh for steam64ids")
        self.rip_server.steam64ids_force_update()
        await ctx.author.send("Done.")
 
    @commands.command(name="map")
    async def map(self, ctx):
        map = self.rip_server.get_map(config['battlemetrics']['server'])
        await ctx.author.send(f"Current map: {map}")

    @tasks.loop(minutes=1)
    async def balance_check(self):
        print("! balance check")
        print(f"- minutes since map change: {self.minutes_since_mapchange}")
        # no warnings on friday
        if date.today().isoweekday() == 5:
            return
        # only allowed to warn imbalances at beginning of round.
        if self.minutes_since_mapchange > LATEST_ROUND_TIME_FOR_REMINDER:
            return
        if self.minutes_since_mapchange < EARLIEST_ROUND_TIME_FOR_REMINDER:
            return
        # do not remind if not enough time has passed
        if self.minutes_since_mapchange - self.reminder_sent_at < WAIT_TIME_BETWEEN_REMINDERS:
            return
        # only allow a max set of reminders
        if self.reminders_sent > MAX_IMBALANCE_REMINDERS:
            return

        team_balances = self.rip_server.rip_balance()

        balance_left = team_balances.get(1, 0)
        balance_right = team_balances.get(2, 0)
        balance_difference = abs(balance_left - balance_right)

        if balance_difference > IMBALANCE_DIFFERENCE_ALLOWED:  
            # inacceptable imbalance detected
            print(f"@here RIP server is imbalanced! ({balance_left}v{balance_right}). Fix it plzkthx.")
            await self.rip_squad_channel.send(f"@here RIP server is imbalanced! ({balance_left}v{balance_right}). Fix it plzkthx.")
            await self.online()
            self.reminders_sent += 1
            self.reminder_sent_at = self.minutes_since_mapchange


    @tasks.loop(minutes=1)
    async def update_mapchange(self):
        current_map = self.rip_server.get_map(config['battlemetrics']['server'])
        if current_map != self.previous_map:
            # reset counters
            self.minutes_since_mapchange = 0
            self.reminders_sent = 0
            self.reminder_sent_at = 0
            self.previous_map = current_map
        else:
            self.minutes_since_mapchange += 1
        

    @commands.Cog.listener()
    async def on_ready(self):
        self.rip_squad_channel = self.bot.get_channel(self.config['rip']['announce_balance_issue_discord_channel_id'])

        # start tasks
        self.balance_check.start()
        self.update_mapchange.start()


def setup(bot):
    bot.add_cog(ServerCog(bot))

