from datetime import datetime
import json

import requests

from .battlemetrics import BattleMetrics
from config import config

class RipServer(BattleMetrics):

    def __init__(self, config):
        self.steam64ids_force_update()
        self.steam64ids_uri = config['rip']['steamids_uri']
        super(RipServer, self).__init__(config['battlemetrics']['token'])

    #
    # Server Insights
    #

    def rip_balance(self):
        """Queries the server and returns the RIP member server balance as a dictionary."""
        self.steam64ids_ensure_freshness()
        teams = self.get_teams_rip_only()

        balance = {}
        for team_id in teams:
            side_count = len(teams[team_id])
            balance[team_id] = side_count

        return balance

    
    def get_teams_rip_only(self):
        """Queries the server and returns a list of all RIP members on each team."""
        identities = self.get_identities(config['battlemetrics']['server'], "steamID")
        teams = self.get_teams(config['battlemetrics']['server'])

        for team_id in teams:
            team = teams[team_id]
            teams[team_id] = list(filter(lambda p: identities[p.id][0].attributes.identifier in self.steam64ids, team))
        
        return teams


    #
    # Steam64ID Management
    #

    def steam64ids_ensure_freshness(self):
        """Ensures the age of the list of steam IDs is below a set amount of hours. 
        Refetches the list if necessary. """
        delta = datetime.now() - self.steam64ids_updated_at
        if (delta.total_seconds()/3600) > config['rip']['steamids_update_interval']:
            print("Steam64ids not fresh. updating.")
            self.steam64ids_force_update()
    
    def steam64ids_force_update(self):
        """Force a refetch of the list of steam IDs."""
        self.steam64ids_updated_at = datetime.now()
        self.steam64ids = []
        if config['rip']['steamids_uri']:
            uri = config['rip']['steamids_uri']
            res = requests.get(uri)
            self.steam64ids = []
            for line in res.iter_lines():
                self.steam64ids.append(line.decode('utf-8').strip())
            print('Retrieved SteamID64s from ' + uri)
        else:
            with open('./steam64ids.json') as f:
                self.steam64ids = json.load(f)
            print('Retrieved SteamID64s from local file.')