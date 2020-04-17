from collections import namedtuple
import json

import requests 


class BattleMetrics(object):

    def __init__(self, auth_token):
        self.auth_token = auth_token
    
    def get_teams(self, server_id):
        """Fetch all players from server and seperate them based on their team.

        Keyword arguments:
        server_id -- the battlemetrics ID of the server
        """
        res = self._perform_request(
                self._build_get_request(
                    "/servers/{0}?include=player".format(server_id)))

        teams = {}
        for item in res.included:
            if item.type == 'player':
                item_metadata = item.meta.metadata
                for metadata in item_metadata:
                    if metadata.key == 'teamID':
                        team_id = metadata.value or 0
                teams.setdefault(team_id, []).append(item)

        return teams

    def get_sessions(self, server_id):
        res = self._perform_request(
            self._build_get_request(
                "/servers/{0}?include=session".format(server_id)))

        player_sessions = {}
        for item in res.included:
            player_id = item.relationships.player.data.id
            session_start = item.attributes.start
            player_sessions[player_id] = session_start
        return player_sessions

    def get_identities(self, server_id, identifier_type=None):
        res = self._perform_request(
            self._build_get_request(
                "/servers/{0}?include=identifier".format(server_id)))

        players = {}
        for item in res.included:
            if item.type == 'identifier' and (identifier_type is None or item.attributes.type == identifier_type):
                bm_id = item.relationships.player.data.id
                players.setdefault(bm_id, []).append(item)

        return players

    # - Internal Methods

    def _build_get_request(self, path):
        uri = "https://api.battlemetrics.com" + path
        bearer_header_content = "Bearer " + self.auth_token
        headers = {
            "Authorization": bearer_header_content
        }
        return requests.get(uri, headers=headers)

    def _perform_request(self, req):
        """Performs the request and returns an dot object"""
        
        res = req.content
        x = json.loads(res, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
        return x

