# coding: utf-8
import os
import subprocess
import requests
import codecs
import slackbot_settings
import dropbox
import yaml
from slacker import Slacker
slacker = Slacker(slackbot_settings.API_TOKEN)

with open( "./conf.yml" ) as fy_r:
    conf = yaml.safe_load( fy_r )
home = os.path.expanduser("~") + "/"
loganalyzer_path = home + conf['loganalyzer_path']
tournament_path = home + conf['tournament_path']
sample_config_yml = tournament_path + conf['sample_conf_path']

comp_flag_dict = {}


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


def getTeamsInGroup(group):
  path = ('../../tournament/config/group/' + group + '.txt')
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
    group = setting[0] # ''.join(setting[:6])
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

def upload_file_s( file_path, channel_id ):
  if os.path.exists( file_path ):
    slacker.files.upload( file_=file_path, channels=channel_id )


def loadGroupYml( tournament_conf_path, group, group_conf_path ):
  if os.path.exists( group_conf_path ):
    with open( group_conf_path ) as fy:
      yaml_conf = yaml.safe_load(fy)
  else:
    print('not exist group conf file')

  if os.path.exists( tournament_conf_path ):
    with open( tournament_conf_path ) as fy:
      tournament_conf = yaml.safe_load(fy)
  else:
    print('not exist tournament conf file')

  if group in yaml_conf.keys():
    group_conf = yaml_conf[group]
  else:
    print('not exist ' + group + 'conf')

  for key in group_conf.keys():
    tournament_conf[key] = group_conf[key]

  with open( tournament_conf_path, 'w' ) as fy_w:
    yaml.dump( tournament_conf, fy_w, default_flow_style=False )


def storeGroupYml( group_conf_path, group, key, values ):
  if os.path.exists( group_conf_path ):
    with open( group_conf_path ) as fy:
      yaml_conf = yaml.safe_load(fy)
  else:
    print('not exist file')
    return False

  if group not in yaml_conf.keys():
    yaml_conf[group] = {}

  # if list != type(values):
  #   values = values.split()

  if key in getTourYmlKeys():
    if len(values) == 1:
      yaml_conf[group][key] = values[0]
    else:
      yaml_conf[group][key] = values
  else:
    print(key + ' does not exist in tournament conf')
    return False

  with open( group_conf_path, 'w' ) as fy_w:
    yaml.dump( yaml_conf, fy_w, default_flow_style=False )
  return True


def listGroupYml( path, group, key ):
  if os.path.exists( path ):
    with open( path ) as fy:
      yaml_conf = yaml.safe_load(fy)
  else:
    print('not exist file')
    return False

  if group not in yaml_conf.keys():
    print('not in ' + group + ' config')
    return False
  elif key in yaml_conf[group].keys():
    return yaml_conf[group][key]
  else:
    print('not in')
    return False


def getTourYmlKeys( tournament_conf_path=sample_config_yml ):
  if os.path.exists( tournament_conf_path ):
    with open( tournament_conf_path ) as fy:
      tour_conf = yaml.safe_load(fy)
  else:
    print('not exist ' + tournament_conf_path )
    return []

  return tour_conf.keys()


def writeYml( path, key, values ):
  if os.path.exists( path ):
    with open( path ) as fy:
      yaml_conf = yaml.safe_load(fy)
  else:
    yaml_conf = {}

  yaml_conf[key] = values

  with open( path, 'w' ) as fy_w:
    yaml.dump( yaml_conf, fy_w, default_flow_style=False )


def addYml( path, key, values ):
  if os.path.exists( path ):
    with open( path ) as fy:
      yaml_conf = yaml.safe_load(fy)
  else:
    yaml_conf = {}
    print('not exist yaml file')

  if list != type(values):
    values = values.split()

  if key in yaml_conf.keys():
    for value in values:
      if value not in yaml_conf[key]:
        if list != type(yaml_conf[key]):
          yaml_conf[key] = yaml_conf[key].split()
        yaml_conf[key].append( value )
  else:
    yaml_conf[key] = values

  with open( path, 'w' ) as fy_w:
    yaml.dump( yaml_conf, fy_w, default_flow_style=False )


def deleteYml( path, key, values ):
  if os.path.exists( path ):
    with open( path ) as fy:
      yaml_conf = yaml.safe_load(fy)
  else:
    yaml_conf = {}

  if list != type(values):
    values = values.split()

  for value in values:
    if value in yaml_conf[key]:
      if list != type( yaml_conf[key] ):
        yaml_conf[key] = yaml_conf[key].split()
      yaml_conf[key].remove( value )
    else:
      print( value + ' not in ' + key + ' values')

  with open( path, 'w' ) as fy_w:
    yaml.dump( yaml_conf, fy_w, default_flow_style=False )


def listYml( path, key ):
  flag = False
  if os.path.exists( path ):
    with open( path ) as fy:
      yaml_conf = yaml.safe_load(fy)
    flag = True
  else:
    print('not exist file')

  if flag and key in yaml_conf.keys():
    return yaml_conf[key]
  else:
    return 'not in'


class MyDropbox():
  DB_ACCESS_TOKEN = ''
  DB_ROOT_DIR = ''

  def __init__(self, token, dir_path):
    self.DB_ACCESS_TOKEN = token
    self.DB_ROOT_DIR = dir_path
    self.dbx = dropbox.Dropbox(self.DB_ACCESS_TOKEN)

  def viewFiles(self):
    res = self.dbx.files_list_folder(self.DB_ROOT_DIR, recursive=True)

    self.__get_files_recursive(res)

  def dbox(self):
    print(self.dbx.users_get_current_account())
    setting = dropbox.sharing.SharedLinkSettings(requested_visibility=dropbox.sharing.RequestedVisibility.public)
    print(setting)
    result = self.dbx.files_list_folder(path="")
    for entry in self.dbx.files_list_folder('').entries:
      print(entry.name)

  def createFolder(self):
    dir_flag = False
    dir_path = self.DB_ROOT_DIR
    pre_dir_path = '/'.join(dir_path.split('/')[0:-1])
    print(pre_dir_path)
    for entry in self.dbx.files_list_folder(pre_dir_path, recursive=True).entries:
      if entry.name == dir_path.split('/')[-1]:
        dir_flag = True
        print('exist dir path')
    if not dir_flag:
      self.dbx.files_create_folder_v2(dir_path)
      print('created directory')

  def uploadFiles(self, contents, file_name):
    self.dbx.files_upload( contents, self.DB_ROOT_DIR + '/' + file_name, autorename=True )

  def get_shared_link(self, path):
    return self.__get_shared_link(path)

  def __get_files_recursive(self, res):
    for entry in res.entries:
      ins = type(entry)
      # if ins is not dropbox.files.FileMetadata: #ファイル以外（＝フォルダ）はスキップ
      #     continue

      link = self.__get_shared_link(entry.path_lower)
      if bool(link):
        print(entry.path_display)
        print(link)

    if res.has_more:
      res2 = self.dbx.files_list_folder_continue(res.cursor)
      self.__get_files_recursive(res2)

  def __get_shared_link(self, path):
    links = self.dbx.sharing_list_shared_links(path=path, direct_only=True).links

    if links is not None:
      for link in links:
        return link.url #1件目

    return self.__create_shared_link(path)

  def __create_shared_link(self, path):
    setting = dropbox.sharing.SharedLinkSettings(requested_visibility=dropbox.sharing.RequestedVisibility.public)
    link = self.dbx.sharing_create_shared_link_with_settings(path=path, settings=setting)

    return link.url


if __name__ == '__main__':
    getOpponent()
