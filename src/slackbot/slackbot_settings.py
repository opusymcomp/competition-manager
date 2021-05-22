# coding: utf-8

import yaml
import os

dirname = os.path.dirname(__file__)
with open('{}/../../config/manager.yml'.format(dirname), 'r') as fy_r:
    MANAGER_CONF = yaml.safe_load(fy_r)

COMPETITION_MANAGER_PATH = MANAGER_CONF['competition_manager_path']
LOGANALYZER_PATH = MANAGER_CONF['loganalyzer_path']
TOURNAMENT_PATH = MANAGER_CONF['tournament_path']

DROPBOX_ACCESS_TOKEN = MANAGER_CONF['dropbox_access_token']
DROPBOX_BOOT_DIR = MANAGER_CONF['dropbox_boot_dir']

GOOGLE_DRIVE_CLIENT_ID = MANAGER_CONF['google_drive_client_id']
GOOGLE_DRIVE_CLIENT_SECRET = MANAGER_CONF['google_drive_client_secret']
GOOGLE_DRIVE_FOLDER_ID = MANAGER_CONF['google_drive_folder_id']

DISCORD_TOKEN = MANAGER_CONF['discord_token']
DISCORD_CHANNEL_ID = MANAGER_CONF['discord_channel_id']

ORGANIZER_CHANNEL_NAME = MANAGER_CONF["organizer_channel_name"]
ANNOUNCE_CHANNEL_NAME = MANAGER_CONF['announce_channel_name']

COMPETITION_NAME = MANAGER_CONF['competition_name']
TEAMS_DIR = MANAGER_CONF['teams_dir']
LOG_DIR = MANAGER_CONF['log_dir']

# API Token
# Check your slack workspace settings
API_TOKEN = MANAGER_CONF['slack_api_token']

# Default Reply (when @bot)
DEFAULT_REPLY = 'Mention respond is only supported in DM to me (\'upload\' command is only available).'

# Subdirectory name of plugin scripts
PLUGINS = ['plugins']
