import sys
sys.path.append('../src/slackbot')
from slackbot_settings import *
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import json
import datetime

current_dir = os.getcwd()
os.chdir(COMPETITION_MANAGER_PATH+'config')

gauth = GoogleAuth()
gauth.attr['settings']['client_config']['client_id'] = GOOGLE_DRIVE_CLIENT_ID
gauth.attr['settings']['client_config']['client_secret'] = GOOGLE_DRIVE_CLIENT_SECRET
gauth.CommandLineAuth()
drive = GoogleDrive(gauth)

os.chdir(current_dir)
