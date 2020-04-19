# RIPper bot

## Setup

1. Create a virtual environment 'env'

> python3 -m venv env

2. activate virtual environment

> source env/bin/activate

3. install python requirements

> pip install -r requirements.txt

## Configuration

The bot can be configured either by setting environment variables or using a lcoal `config.json` file. For the local json configuration, please refer to `config.example.json`.

Following environment variables could be set:
- BM_SERVER_TOKEN: the token secret with admin privileges on Battlemetrics
- BM_SERVER_ID: the Battlemetrics ID given to the server to watch
- DISCORD_TOKEN: the discord token to identify with the discord bot
- RIP_STEAMIDS_URI: the link to the text file containing all Steam IDs of RIP members
- RIP_STEAMIDS_UPDATE_HOURS: amount of hours to consider the list of Steam ID's as fresh before performing a new fetch

## Operation

Ensure you have a config.json and steam64ids.json file in the same folder as `bot.py`. Please refer to the respective example files on how to set them up correctly.

### Manual

You can run the bot manually by running the `bot.py` script within the virtualenv.

> python3 bot.py


### Automatic

The repository is equipped with everything required for it to be hosted on heroku.
