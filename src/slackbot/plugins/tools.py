# coding: utf-8
import os
import subprocess
import requests
import codecs
from slackbot_settings import *
import dropbox
import yaml
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from slacker import Slacker

slacker = Slacker(API_TOKEN)

comp_flag_dict = {}


def resCmd(cmd):
    return subprocess.Popen(
        cmd, stdout=subprocess.PIPE,
        shell=True).communicate()[0]


def rsync(from_path, to_path):
    return subprocess.run(['rsync -au {} {}'.format(from_path, to_path)],
                          encoding='utf-8', stdout=subprocess.PIPE, shell=True)


def scp(from_path, to_path):
    return subprocess.run(['scp -r {} {}'.format(from_path, to_path)],
                          encoding='utf-8', stdout=subprocess.PIPE, shell=True)


def cmdAtRemoteServer(server, cmd):
    return subprocess.run(['ssh {} {}'.format(server, cmd)],
                          encoding='utf-8', stdout=subprocess.PIPE, shell=True)


def getHelpMessageForOrganizers():
    msg = '[Command list]\n' \
          ' -team : Show qualified team that succeeded the binary test.\n' \
          ' -clear qualification : Clear qualification.\n' \
          ' -server * : Update IP address for rcssserver. (e.g. server 127.0.0.1)\n' \
          ' -host *,* : Update hosts\' IP addresses for teams. 2 addresses are required. (e.g. host 127.0.0.1,127.0.0.1)\n' \
          ' -register * : Update registered team-list. (e.g. register hogehoge@gmail.com,teamA)\n' \
          ' -group* : Create a group and select teams to run the round-robin. (e.g. groupA teamA,teamB,teamC,...)\n' \
          ' -start group* : Start round-robin. (e.g. start groupA)\n' \
          ' -allow binary upload : Add upload authorization for users registered in /path/to/competition-manager/test/maillist.txt\n' \
          ' -binary upload end : Remove upload autorization for users registered in /path/to/competition-manager/test/maillist.txt\n' \
          ' -test : Test qualified teams. (e.g. test teamA,teamB,teamC,...)\n' \
          ' -stop test : Cancel testing teams\n' \
          ' -announce match: Announce the progress report and match result\n' \
          ' -check matches: Simulate the group matches and announce the schedule\n' \
          ' -dropbox* : Switch dropbox flag whether dropbox will be used or not. (e.g. dropbox true)\n' \
          ' -gdrive* : Switch google_drive flag whether google_drive will be used or not. (e.g. gdrive true)\n' \
          ' -discordbot* : Switch discordbot flag whether discord_bot will be used or not. (e.g. discordbot true)\n' \
          ' -share* : Send files to the cloud storage. Choose \'teams\' or \'logs\' as an argument (e.g. share teams)\n' \
          ' -recovery mode * : Switch recovery mode that can change game flag and binary test queue. (e.g. recovery mode true)\n' \
          ' -reset gameflag: Reset game flag. Please check rcssserver state before use this (! this command is only available during recovery mode!)\n' \
          ' -reset test queue * : Remove the specified team from the binary test queue. (! this command is only available during recovery mode!)'
    return msg


def getHelpMessageForAnnounce():
    msg = 'commnand \'help\' is not supported in this channel.'
    return msg


def getHelpMessageForDM():
    msg = 'You can only use \'upload\' command in DM. (e.g. upload teamA)\n' \
          'Please refer to https://docs.google.com/document/d/1J2Pml2NStNWkRi4zZUVr_1SC9DxyJDOmTrwSMAPzSXQ/edit?usp=sharing'
    return msg


def getHelpMessageUnsupported():
    msg = 'commnand \'help\' is not supported in this channel.'
    return msg


def getQualifiedTeams():
    if os.path.exists('{}config/qualification.txt'.format(COMPETITION_MANAGER_PATH)):
        with open('{}config/qualification.txt'.format(COMPETITION_MANAGER_PATH), 'r') as q_txt:
            qualified_teams = q_txt.readlines()
        for i in range(len(qualified_teams)):
            qualified_teams[i] = qualified_teams[i].replace('\n', '').split(',')[0]
    else:
        qualified_teams = []
    return qualified_teams


def getStartgroup(startgroup):
    startgroup = ''.join(startgroup[6:])
    print('startgroup', startgroup)
    gtxt = startgroup + '.txt'
    path = ('{}config/group/{}'.format(TOURNAMENT_PATH, gtxt))
    f = open(path, mode='r+')
    datalist = [s.split(',') for s in f.readlines()][0]
    f.close()
    return datalist


def getChannelID(message, name):
    for id_num, info in message.channel._client.channels.items():
        if name == info['name']:
            return id_num


def isChannelMembers(message, channel_name):
    channel_id = getChannelID(message, channel_name)
    return message.channel._client.channels[channel_id]['is_member']


def upload_file(channel_id, file_path, comment):
    file_name = os.path.basename(file_path)
    param = {
        'token': API_TOKEN,
        'channels': channel_id,
        'filename': file_name,
        'initial_comment': comment,
        'title': file_name
    }
    files = {
        'file': open(file_path, 'rb')
    }
    upload_url = "https://slack.com/api/files.upload"
    requests.post(url=upload_url, params=param, files=files)


def upload_file_s(file_path, channel_id):
    if os.path.exists(file_path):
        slacker.files.upload(file_=file_path, channels=channel_id)


def loadYml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def saveYml(yaml_conf, path):
    with open(path, 'w') as f:
        yaml.dump(yaml_conf, f, default_flow_style=False)


def overwriteYml(path, added_info):
    if os.path.exists(path):
        yaml_conf = loadYml(path)
    else:
        print('({}) {} is not exist'.format(overwriteYml.__name__, path))
        print('({}) create new yml file'.format(overwriteYml.__name__))
        yaml_conf = {'hosts': ['', ''],
                     'log_dir': 'log',
                     'match_sleep': 2,
                     'mode': 'group',
                     'player_conf': 'config/rcssserver/player_official.conf'.format(TOURNAMENT_PATH),
                     'server_conf': 'config/rcssserver/server_official.conf'.format(TOURNAMENT_PATH),
                     'shutdown_sleep': 2,
                     'team_mode': 'official',
                     'teams': ['', ''],
                     'teams_dir': os.environ['HOME'],
                     'title': COMPETITION_NAME
                     }

    for key, value in added_info.items():
        yaml_conf[key] = value

    saveYml(yaml_conf, path)


def startGame(server, yml):
    result = cmdAtRemoteServer(server, 'cd tournament; ./start.sh --config={}'.format(yml))
    return result


def startSimulate(server, yml):
    result = cmdAtRemoteServer(server, 'cd tournament; ./start.sh --config={} --simulate'.format(yml))
    return result


def getTeamsInGroup(group):
    teams_in_group = []
    if os.path.exists('{}config/group.yml'.format(COMPETITION_MANAGER_PATH)):
        group_yaml = loadYml('{}config/group.yml'.format(COMPETITION_MANAGER_PATH))
        if group in group_yaml.keys():
            teams_in_group = group_yaml[group]
    return teams_in_group


def getResults(result_file):
    with open(result_file, 'r') as r_log:
        log_lines = r_log.readlines()
    header = log_lines[0].split(',')
    elm = log_lines[-1].split(',')
    return {header[i].strip(): elm[i].strip() for i in range(len(header))}


def getMatchStartMessage(match_dict, focused_game_id):
    msg = match_dict['match_' + str(focused_game_id)]['team_l'] + ' vs ' \
          + match_dict['match_' + str(focused_game_id)]['team_r']
    return msg


def getMatchResultMessage(match_dict, result_dict, focused_game_id):
    msg = match_dict['match_' + str(focused_game_id)]['team_l'] + '_' \
          + result_dict['left score'] + ' vs ' \
          + result_dict['right score'] + '_' \
          + match_dict['match_' + str(focused_game_id)]['team_r']
    return msg


def getGroupMatchListMessage(group):
    teams = getTeamsInGroup(group)
    tmp_setting = {'teams': teams,
                   'log_dir': 'tmp'}

    # save as tmp yml in order to avoid overwriting the current tournament configuration
    tmp_yml_name = '{}config/check_matches.yml'.format(COMPETITION_MANAGER_PATH)
    overwriteYml(tmp_yml_name, tmp_setting)
    group_match_sim = startSimulate(tmp_yml_name.format(COMPETITION_MANAGER_PATH))
    tmp_yml = loadYml(tmp_yml_name)
    os.remove(tmp_yml_name.format(COMPETITION_MANAGER_PATH))

    print(group_match_sim.stdout)

    matches = group_match_sim.stdout.split("\n")
    msg = ''
    for i in range(len(matches) - 2):
        if i == 0:
            continue
        elif i == 1:
            matches[i] = matches[i].replace('group', group)
        else:
            mod_row = matches[i].split()
            mod_row[1] = mod_row[1].replace(tmp_yml['teams_dir'] + '/', '')
            mod_row[3] = mod_row[3].replace(tmp_yml['teams_dir'] + '/', '')
            matches[i] = " ".join(mod_row)
        msg += matches[i] + '\n'

    return msg


def checkRegistration(registration_txt, email, teamname):
    list_flag = False
    only_mail_flag = False
    only_team_flag = False
    tmp_team = None

    with open(registration_txt, mode='rt', encoding='utf-8') as f:
        for line in f:
            if line == '\n':
                continue
            if line[0] == '#':
                continue
            l_mail, l_team = line.strip().split(',')
            if l_mail == email and l_team == teamname:
                list_flag = True
                # break
            if l_mail == email:
                only_mail_flag = True
                tmp_team = l_team
                # break
            if l_team == teamname:
                only_team_flag = True
                # break

    return list_flag, only_mail_flag, only_team_flag, tmp_team


def sendMessageToChannels(message, message_str, channels, default_id):
    for channel in channels:
        message.body['channel'] = channel
        message.send(message_str)
    # set default
    message.body['channel'] = default_id


def sendMessageToDiscordChannel(message_str):
    p = subprocess.run(['python {}src/discordbot/run.py \'{}\''.format(COMPETITION_MANAGER_PATH, message_str)],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         shell=True)
    if p.returncode == 0:
        print('Send message to discord successfully.')
    else:
        print('Sending message to discord is failed.')


class MyDropbox(object):
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

    def createFolder(self, path):
        dir_path = path  # self.DB_ROOT_DIR
        # print(dir_path)
        depth_path = ''
        # for entry in self.dbx.files_list_folder(depth_path, recursive=True).entries:
        #   #print(entry)
        #   if entry.name == dir_path.split('/')[-1]:
        #     dir_flag = True
        #     print('exist dir path')
        # if not dir_flag:
        #   self.dbx.files_create_folder_v2(dir_path)
        #   print('created directory')
        for depth in dir_path.split('/')[1:]:
            dir_flag = False
            print('pre_entry: ' + depth_path)
            depth_entries = self.dbx.files_list_folder(depth_path).entries
            depth_path = depth_path + '/' + depth
            print('depth_path: ' + depth_path.split('/')[-1])
            for entry in depth_entries:
                print('entry: ' + entry.name)
                if entry.name == depth_path.split('/')[-1]:
                    dir_flag = True
                    print('exist dir path')
                    break
            if not dir_flag:
                self.dbx.files_create_folder_v2(depth_path)
                print('created directory')
        print(dir_path)

        # pre_dir_path = '/'.join(dir_path.split('/')[0:-1])
        # print(pre_dir_path)
        # for entry in self.dbx.files_list_folder(pre_dir_path, recursive=True).entries:
        #   if entry.name == dir_path.split('/')[-1]:
        #     dir_flag = True
        #     print('exist dir path')
        # if not dir_flag:
        #   self.dbx.files_create_folder_v2(dir_path)
        #   print('created directory')

    def uploadFiles(self, contents, file_name):
        self.dbx.files_upload(contents, self.DB_ROOT_DIR + '/' + file_name, autorename=True)

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
                return link.url  # 1件目

        return self.__create_shared_link(path)

    def __create_shared_link(self, path):
        setting = dropbox.sharing.SharedLinkSettings(requested_visibility=dropbox.sharing.RequestedVisibility.public)
        link = self.dbx.sharing_create_shared_link_with_settings(path=path, settings=setting)

        return link.url


class MyGoogleDrive(object):
    def __init__(self):
        current_dir = os.getcwd()
        os.chdir(COMPETITION_MANAGER_PATH + 'config')

        self.gauth = GoogleAuth()
        self.gauth.attr['settings']['client_config']['client_id'] = GOOGLE_DRIVE_CLIENT_ID
        self.gauth.attr['settings']['client_config']['client_secret'] = GOOGLE_DRIVE_CLIENT_SECRET
        self.gauth.CommandLineAuth()
        self.drive = GoogleDrive(self.gauth)
        self.folder_id = GOOGLE_DRIVE_FOLDER_ID

        os.chdir(current_dir)

    def upload(self, path, prefix=None):
        if len(path) != 0 and path[-1] == '/':
            local_data_path = path[:-1]
        else:
            local_data_path = path

        if not prefix:
            t_folder = self.__createDir(GOOGLE_DRIVE_FOLDER_ID, os.path.basename(local_data_path))
        else:
            splitted_prefix = prefix.split('/')
            for i, p in enumerate(splitted_prefix):
                if i == 0:
                    t_folder = self.__createDir(GOOGLE_DRIVE_FOLDER_ID, p)
                else:
                    t_folder = self.__createDir(t_folder['id'], p)
            t_folder = self.__createDir(t_folder['id'], os.path.basename(local_data_path))
        self.__upload_recursive(t_folder, local_data_path)

    def __upload_recursive(self, parent_directory, path):
        dir_list = self.__getDirList(path)
        if len(dir_list) == 0:
            file_list = self.__getFileList(path)
            for f in file_list:
                self.__uploadFile(parent_directory['id'], f)
        else:
            for d in dir_list:
                d_folder = self.__createDir(parent_directory['id'], os.path.basename(d))
                self.__upload_recursive(d_folder, path + '/' + os.path.basename(d))

    def __createDir(self, pid, fname):
        ret = self.__checkFiles(pid, fname)
        if not ret:
            folder = self.drive.CreateFile({'title': fname, 'mimeType': 'application/vnd.google-apps.folder'})
            folder['parents'] = [{'id': pid}]
            folder.Upload()
        else:
            folder = ret
            print(folder['title'] + " exists")

        return folder

    def __uploadFile(self, pid, fname):
        ret = self.__checkFiles(pid, fname)
        if not ret:
            gf = self.drive.CreateFile()
            gf['parents'] = [{'id': pid}]
            gf.SetContentFile(fname)
            gf['title'] = os.path.basename(fname)
            gf.Upload()
        else:
            gf = ret
            print(gf['title'] + " exists")
        return gf

    def __checkFiles(self, pid, fname):
        query = '"{}" in parents and trashed = false'.format(pid)
        query += ' and title = "' + os.path.basename(fname) + '"'

        list = self.drive.ListFile({'q': query}).GetList()
        if len(list) > 0:
            return list[0]
        return False

    @staticmethod
    def __getDirList(basedir):
        files = os.listdir(basedir)
        ret = [os.path.join(basedir, f) for f in files if os.path.isdir(os.path.join(basedir, f))]
        return ret

    @staticmethod
    def __getFileList(basedir):
        files = os.listdir(basedir)
        ret = [os.path.join(basedir, f) for f in files if os.path.isfile(os.path.join(basedir, f))]
        return ret


if __name__ == '__main__':
    pass
