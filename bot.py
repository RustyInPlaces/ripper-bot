import json
import os
from datetime import datetime
import discord
import requests

from battlemetrics import BattleMetrics

#
# Config Retrieval
#

config = {}
config['token'] = os.environ.get('DISCORD_TOKEN')
config['battlemetrics'] = {
    'token': os.environ.get('BM_SERVER_TOKEN'),
    'server': os.environ.get('BM_SERVER_ID')
}
config['rip'] = {
    'steamids_uri': os.environ.get('RIP_STEAMIDS_URI')
}

# local config.json take precedence over set environment variables.
try:
    with open('./config.json', 'r') as f:
        config_json = json.load(f)
        config.update(config_json)
except FileNotFoundError:
    print('No config.json file found. Falling back to ENV VARs')

#
# Fetch steam64ids
#

if config['rip']['steamids_uri']:
    uri = config['rip']['steamids_uri']
    res = requests.get(uri)
    steam64ids = []
    for line in res.iter_lines():
        steam64ids.append(line.decode('utf-8').strip())
        print(steam64ids)
    print('Retrieved SteamID64s from ' + uri)
else:
    with open('./steam64ids.json') as f:
        steam64ids = json.load(f)
    print('Retrieved SteamID64s from local file.')



TEAM_TRANSLATION = {
    1: "left side faction",
    2: "right side faction",
    0: "unassigned"
}

bm = BattleMetrics(
    config['battlemetrics']['token']
)


class RIPClient(discord.Client):

    async def on_ready(self):
        print('Logged on as {0}'.format(self.user))

    async def on_message(self, message):
        if message.content.startswith('!ripbalance'):
            team_balances = self._check_rip_balance()

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

            await message.channel.send(msg)



        elif message.content.startswith('!online'):
            teams = self.get_teams_with_only_rip()
            sessions = bm.get_sessions(config['battlemetrics']['server'])

            if not teams:
                await message.channel.send("Server empty.")
                return

            msg = "RIP Members online (with join time):\n"
            for team_id in sorted(teams.keys()):
                msg += "{0}\n".format(TEAM_TRANSLATION[team_id])

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
            
            await message.channel.send(msg)

    def get_teams_with_only_rip(self):
        identities = bm.get_identities(config['battlemetrics']['server'], "steamID")
        teams = bm.get_teams(config['battlemetrics']['server'])

        for team_id in teams:
            team = teams[team_id]
            teams[team_id] = list(filter(lambda p: identities[p.id][0].attributes.identifier in steam64ids, team))
        
        return teams

 
    def _check_rip_balance(self):
        teams = self.get_teams_with_only_rip()

        balance = {}
        for team_id in teams:
            side_count = len(teams[team_id])
            balance[team_id] = side_count

        return balance


client = RIPClient()
client.run(config['token'])