# coding: utf-8
import os
import subprocess
import requests
import codecs
import slackbot_settings
from slacker import Slacker
slacker = Slacker(slackbot_settings.API_TOKEN)

def resCmd(cmd):
  return subprocess.Popen(
      cmd, stdout=subprocess.PIPE,
      shell=True).communicate()[0]

def getOpponent():
    cmd = ("cat ../../test/qualification.txt")
    settinglist = resCmd(cmd).decode('utf-8').strip().split()
    return settinglist

def getRoundrobin(setting ,gtxt):
    data = ''.join(setting[7:])
    path = ('../../tournament/config/group/'+gtxt)
    f = open(path, mode='w+')
    f.write(data)
    f.close()
    return data

def getStartgroup(startgroup):
    startgroup =  ''.join(startgroup[6:])
    print('startgroup',startgroup)
    gtxt = startgroup + '.txt'
    path = ('../../tournament/config/group/'+gtxt)
    f = open(path, mode='r+')
    datalist = [s.split(',') for s in f.readlines()][0]
    f.close()
    return datalist

def saveGroup(setting):
    currentpath = os.getcwd()
    #home = os.environ['HOME']
    if not os.path.isdir('../../tournament/config/group'):
      os.makedirs('../../tournament/config/group')
    os.chdir("../../tournament/config/group")
    group =  ''.join(setting[:6])
    gtxt = group + '.txt'
    cmd = 'touch %s' % gtxt
    subprocess.run(cmd, shell=True)
    print ('gtxt:',gtxt)
    os.chdir(currentpath)
    return gtxt

def getChannelID( message, name ):
  for id_num, info in message.channel._client.channels.items():
    if name == info['name']:
      return id_num

def getChannelMembers( message, channel_name ):
  channel_id = getChannelID(message, channel_name)
  return message.channel._client.channels[channel_id]['members']

def upload_file( channel_id, file_path, comment ):
  file_name = os.path.basename(file_path)
  param = {
    'token':slackbot_settings.API_TOKEN,
    'channels':channel_id,
    'filename':file_name,
    'initial_comment':comment,
    'title':file_name
  }
  files = {
    'file': open(file_path, 'rb')
  }
  upload_url = "https://slack.com/api/files.upload"
  requests.post( url=upload_url, params=param, files=files)

if __name__ == '__main__':
    getOpponent()
