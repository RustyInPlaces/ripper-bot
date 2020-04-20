import json
import os

#
# Config Retrieval via Environment Variables
#

config = {}
config['token'] = os.environ.get('DISCORD_TOKEN')
config['battlemetrics'] = {
    'token': os.environ.get('BM_SERVER_TOKEN'),
    'server': os.environ.get('BM_SERVER_ID')
}
config['rip'] = {
    'steamids_uri': os.environ.get('RIP_STEAMIDS_URI'),
    'steamids_update_interval':  os.environ.get('RIP_STEAMIDS_UPDATE_HOURS')
}

# local config.json take precedence over set environment variables.
try:
    with open('./config.json', 'r') as f:
        config_json = json.load(f)
        config.update(config_json)
except FileNotFoundError:
    print('No config.json file found. Falling back to ENV VARs')