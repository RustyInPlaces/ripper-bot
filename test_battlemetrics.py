import json 
from battlemetrics import BattleMetrics

with open('./config.json', 'r') as f:
    config = json.load(f)
server_id = config['battlemetrics']['server']

bm = BattleMetrics(
    config['battlemetrics']['token']
)

print('T: GET SESSIONS')
print(bm.get_sessions(server_id))

print('T: GET TEAMS')
print(bm.get_teams(server_id))

print('T: GET IDENTIFIERS')
print(bm.get_identities(server_id, "steamID"))