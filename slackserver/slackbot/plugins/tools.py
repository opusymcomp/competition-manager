# coding: utf-8
import os
import subprocess
import requests
import codecs
import slackbot_settings
import dropbox
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
