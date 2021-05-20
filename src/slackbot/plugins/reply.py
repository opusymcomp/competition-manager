# coding: utf-8
import datetime
import subprocess
import os
import shutil
from distutils.dir_util import copy_tree
from slackbot.bot import respond_to
from slackbot.bot import listen_to
from plugins.utils import in_channel
from slackbot_settings import *
from plugins import tools as tl
from plugins import bin_download as dl

from time import sleep

bin_flag = False
dbx_flag = False
google_drive_flag = False
discordbot_flag = False
announce_flag = False
game_flag = False


if dbx_flag:
    db = tl.MyDropbox(DROPBOX_ACCESS_TOKEN, DROPBOX_BOOT_DIR)
    db.createFolder(DROPBOX_BOOT_DIR)


if os.environ.get("PATH"):
    os.environ["PATH"] = LOGANALYZER_PATH + ":" + os.environ["PATH"]
else:
    os.environ["PATH"] = LOGANALYZER_PATH


@listen_to(r'^help$')
def listen_func(message):
    channel_name = message.channel._body['name']
    if channel_name == ORGANIZER_CHANNEL_NAME:
        msg = tl.getHelpMessageForOrganizers()
    elif channel_name == ANNOUNCE_CHANNEL_NAME:
        msg = tl.getHelpMessageForAnnounce()
    else:
        msg = tl.getHelpMessageUnsupported()
    message.reply(msg)


@respond_to(r'^help$')
def listen_func(message):
    try:
        channel_name = message.channel._body['name']
        if channel_name == ORGANIZER_CHANNEL_NAME:
            msg = tl.getHelpMessageForOrganizers()
        elif channel_name == ANNOUNCE_CHANNEL_NAME:
            msg = tl.getHelpMessageForAnnounce()
        else:
            msg = tl.getHelpMessageUnsupported()
    except KeyError:
        msg = tl.getHelpMessageForDM()
    message.reply(msg)


@listen_to(r'^team$')
@in_channel(ORGANIZER_CHANNEL_NAME)
def listen_func(message):
    msg = 'Qualified teams:\n'
    q_teams_list = tl.getQualifiedTeams()
    for i in range(len(q_teams_list)):
        msg = msg + str(i + 1) + ' : ' + q_teams_list[i] + '\n'
    message.reply(msg)


@listen_to(r'^group\w*')
@in_channel(ORGANIZER_CHANNEL_NAME)
def listen_func(message):
    setting = message.body['text'].split()
    if len(setting) == 1:
        if setting[0] == 'group':
            ans_flag = 'all'
        else:
            ans_flag = 'specify'
    elif len(setting) == 2:
        ans_flag = 'set'
    else:
        ans_flag = 'help'

    if ans_flag == 'help':
        message.reply(tl.getHelpMessageForOrganizers())
        return

    elif ans_flag == 'all':
        if not os.path.exists('{}config/group.yml'.format(COMPETITION_MANAGER_PATH)):
            msg = 'No group.yml. Please use \'group\' commands (e.g. groupA teamA,teamB,teamC).\n'
            msg += tl.getHelpMessageForOrganizers()
            message.reply(msg)
            return
        group_yaml = tl.loadYml('{}config/group.yml'.format(COMPETITION_MANAGER_PATH))
        msg = ''
        for key, value in group_yaml.items():
            msg += key + '\n-' + ','.join(value) + '\n'
        message.send(msg)
        return

    elif ans_flag == 'specify':
        if not os.path.exists('{}config/group.yml'.format(COMPETITION_MANAGER_PATH)):
            msg = 'No group.yml. Please use \'group\' commands (e.g. groupA teamA,teamB,teamC).\n'
            msg += tl.getHelpMessageForOrganizers()
            message.reply(msg)
            return
        group_yaml = tl.loadYml('{}config/group.yml'.format(COMPETITION_MANAGER_PATH))
        try:
            msg = setting[0] + '\n-' + ','.join(group_yaml[setting[0]]) + '\n'
        except Exception:
            msg = '{} is not registered'.format(setting[0])
        message.send(msg)
        return

    elif ans_flag == 'set':
        team_list = setting[1].split(',')
        qualified_teams = tl.getQualifiedTeams()

        for team in team_list:
            if team not in qualified_teams:
                message.reply('{} is not a qualified team. Cannot register {} in {}'.format(team, team, setting[0]))
                team_list.remove(team)

        if len(team_list) >= 2:
            if os.path.exists('{}config/group.yml'.format(COMPETITION_MANAGER_PATH)):
                group_yaml = tl.loadYml('{}config/group.yml'.format(COMPETITION_MANAGER_PATH))
                group_yaml[setting[0]] = team_list
            else:
                group_yaml = {setting[0]: team_list}
            tl.saveYml(group_yaml, '{}config/group.yml'.format(COMPETITION_MANAGER_PATH))
            message.reply('{} is saved'.format(setting[0]))
        else:
            msg = 'The number of registered teams must be 2 or more.'
            message.reply(msg)


@listen_to(r'^host*')
@in_channel(ORGANIZER_CHANNEL_NAME)
def listen_func(message):
    setting = message.body['text'].split()
    if len(setting) == 1:
        if setting[0] == 'host':
            ans_flag = 'status'
        else:
            ans_flag = 'help'
    elif len(setting) == 2:
        ans_flag = 'set'
    else:
        ans_flag = 'help'

    if ans_flag == 'help':
        message.reply(tl.getHelpMessageForOrganizers())
        return

    elif ans_flag == 'status':
        if os.path.exists('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH)):
            tournament_yml = tl.loadYml('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH))
            msg = 'host\n-' + ','.join(tournament_yml['hosts'])
        else:
            msg = '{}config/tournament.yml is not exist. Please set hosts by \'host\' command (e.g. host 127.0.0.1,127.0.01)\n'.format(COMPETITION_MANAGER_PATH)
            msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    elif ans_flag == 'set':
        host_list = setting[1].split(',')
        if len(host_list) == 2:
            host_yaml = {'hosts': host_list}
            tl.overwriteYml('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH), host_yaml)
            tl.overwriteYml('{}config/qualification_test.yml'.format(COMPETITION_MANAGER_PATH), host_yaml)
            message.reply('hosts are updated')
        else:
            msg = 'The number of hosts must be 2'
            message.reply(msg)


@listen_to(r'^server*')
@in_channel(ORGANIZER_CHANNEL_NAME)
def listen_func(message):
    setting = message.body['text'].split()
    if len(setting) == 1:
        if setting[0] == 'server':
            ans_flag = 'status'
        else:
            ans_flag = 'help'
    elif len(setting) == 2:
        ans_flag = 'set'
    else:
        ans_flag = 'help'

    if ans_flag == 'help':
        message.reply(tl.getHelpMessageForOrganizers())
        return

    elif ans_flag == 'status':
        if os.path.exists('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH)):
            tournament_yml = tl.loadYml('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH))
            msg = 'server\n-' + tournament_yml['server']
        else:
            msg = '{}config/tournament.yml is not exist. Please set server by \'server\' command (e.g. server 127.0.0.1)\n'.format(COMPETITION_MANAGER_PATH)
            msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    elif ans_flag == 'set':
        server = setting[1]
        server_yaml = {'server': server}
        tl.overwriteYml('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH), server_yaml)
        tl.overwriteYml('{}config/qualification_test.yml'.format(COMPETITION_MANAGER_PATH), server_yaml)
        message.reply('server is updated')


@listen_to(r'^start \w+')
@in_channel(ORGANIZER_CHANNEL_NAME)
def cool_func(message):
    global game_flag
    if game_flag:
        message.reply('a game is conducted now.')
        return

    if bin_flag:
        message.reply('Binary upload must be prohibit. \'upload end\'')
        return

    # startgroup = message.body['text']
    # group = ''.join(startgroup[6:])

    txt_list = message.body['text'].split()
    if len(txt_list) == 2 and 'group' in txt_list[1]:
        group = txt_list[1]
    else:
        msg = tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    tournament_conf = {}
    dt_start = datetime.datetime.now().strftime('%Y%m%d%H%M')

    if len(txt_list) == 2 and 'group' in group:
        if os.path.exists('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH)):
            teams = tl.getTeamsInGroup(group)
            if len(teams) == 0:
                msg = '\'{}\' is empty. Please create groups by \'group\' command before using this command.'.format(group)
                message.reply(msg)
                return
            tournament_conf['log_dir'] = '{}/{}'.format(dt_start, group)
            tournament_conf['teams'] = teams
        else:
            message.reply('{}config/tournament.yml does not exist. Please setup tournament settings by '
                          '\'server\' and \'host\' commands before using this command'.format(COMPETITION_MANAGER_PATH))
            return
    else:
        message.reply(tl.getHelpMessageForOrganizers())
        return

    tl.overwriteYml('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH), tournament_conf)

    msg = 'The ' + group + ' starts soon \n Start time : ' + dt_start + '\n I will notify you when the game ' \
                                                                        'finished.\n '
    message.reply(msg)
    message.react('+1')
    original_channel_id = message.body['channel']
    announce_channel_id = tl.getChannelID(message, ANNOUNCE_CHANNEL_NAME)
    tl.sendMessageToChannels(message=message,
                             message_str=msg,
                             channels=[original_channel_id, announce_channel_id],
                             default_id=original_channel_id)
    if discordbot_flag:
        tl.sendMessageToDiscordChannel(msg)

    game_flag = True
    conf = tl.loadYml('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH))

    """
    if conf['mode'] == 'single_match':
        for num_l in range(len(roundrobin) - 1):
            for num_r in range(num_l + 1, len(roundrobin)):
                dt_now_M = datetime.datetime.now().strftime('%Y%m%d%H%M')

                matchteam = []
                matchteam.append(roundrobin[num_l])
                matchteam.append(roundrobin[num_r])

                # with open( '{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH) ) as fy_r:
                #     conf = yaml.safe_load( fy_r )
                conf['teams'] = matchteam
                log_d = conf['log_dir'].split('/')

                # log/a/などの様に前後に空の要素が出来るときの処理
                for i in range(log_d.count("")):
                    log_d.remove("")

                conf['log_dir'] = ""
                find_g = [s for s in log_d if "group" in s]
                if len(find_g) > 0:
                    for n in range(len(log_d)):
                        if "group" in log_d[n]:
                            break
                        conf['log_dir'] = conf['log_dir'] + log_d[n] + '/'
                else:
                    for n in range(len(log_d)):
                        conf['log_dir'] = conf['log_dir'] + log_d[n] + '/'
                conf['log_dir'] = conf['log_dir'] + group + '/' + dt_now_M

                with open('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH), 'w') as fy_w:
                    yaml.dump(conf, fy_w, default_flow_style=False)
                msg = 'match start' + str(matchteam)
                message.send(msg)

                subprocess.run([tournament_path + 'start.sh', '--config=' + config])

                # arg=[]
                # arg.append(tournament_path)
                # arg.append(conf['log_dir'])
                # arg.extend(roundrobin)
                # arg = " ".join(arg)
                # result = subprocess.run( ['../gametools/results/result.sh', str(arg)] )

                rank = subprocess.run(['../gametools/results/rank.sh', str(group)], encoding='utf-8',
                                      stdout=subprocess.PIPE)
                print(rank.stdout)
                # standing.main(group)

                msg = 'match finish' + str(matchteam)
                message.send(msg)
    """

    if conf['mode'] == 'group':
        # update tournament.yml
        tl.saveYml(conf, '{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH))

        # simulate
        group_match_sim = tl.startSimulate('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH))

        # save match list
        match_dict = {}
        max_match = 0
        matches = group_match_sim.stdout.split('\n')

        for i in range(len(matches)):
            if 'vs' in matches[i]:
                match_line = matches[i].split()
                match_name = 'match_' + match_line[0].rstrip(':')
                match_team = {}
                match_team['team_l'] = match_line[1].split('/')[-1]
                match_team['team_r'] = match_line[3].split('/')[-1]
                match_dict[match_name] = match_team
                max_match = max(max_match, int(match_line[0].rstrip(':')))
        match_dict['max_match'] = max_match
        tl.saveYml(match_dict, '{}config/match_list.yml'.format(COMPETITION_MANAGER_PATH))

        # start game
        _ = tl.startGame('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH))

        # wait for sending match-end message
        sleep(10)

        # copy the game log files
        os.makedirs(LOG_DIR, exist_ok=True)
        copy_tree('{}{}'.format(TOURNAMENT_PATH, dt_start), LOG_DIR)
        os.makedirs(LOG_DIR + 'archive/', exist_ok=True)
        shutil.move('{}{}'.format(TOURNAMENT_PATH, dt_start), '{}archive'.format(LOG_DIR))

    else:
        msg = 'Illegal game mode \'{}\'.'.format(conf['mode'])
        message.reply(msg)
        return

    dt_finish = datetime.datetime.now().strftime('%Y%m%d%H%M')
    msg = 'The ' + group + ' finish! \n Finish time : ' + dt_finish

    if dbx_flag:
        db_g_link = db.get_shared_link(DROPBOX_BOOT_DIR + '/' + group)
        msg += '\n' + db_g_link

    if google_drive_flag:
        gdrive = tl.MyGoogleDrive()
        gdrive.upload(LOG_DIR)
        msg += '\n https://drive.google.com/drive/folders/{}'.format(GOOGLE_DRIVE_FOLDER_ID)

    tl.sendMessageToChannels(message=message,
                             message_str=msg,
                             channels=[original_channel_id, announce_channel_id],
                             default_id=original_channel_id)
    if discordbot_flag:
        tl.sendMessageToDiscordChannel(msg)

    game_flag = False


@listen_to(r'^announce match$')
@in_channel(ORGANIZER_CHANNEL_NAME)
def listen_func(message):
    if not os.path.exists('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH)):
        msg = 'No tournament.yml. Please use \'server\', \'host\' and \'group\' commands before use this command.\n'
        msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    conf = tl.loadYml('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH))
    tournament_log_dir = '{}{}/'.format(TOURNAMENT_PATH, conf['log_dir'])
    match_dict = tl.loadYml('{}config/match_list.yml'.format(COMPETITION_MANAGER_PATH))

    match_n = 0

    original_channel_id = message.body['channel']
    announce_channel_id = tl.getChannelID(message, ANNOUNCE_CHANNEL_NAME)

    progress_flag = False
    global announce_flag
    announce_flag = True
    while game_flag:
        if os.path.exists(tournament_log_dir):
            for n in os.listdir(tournament_log_dir):
                if 'match' in n:
                    num = n[len('match_'):]
                    if match_n < int(num):
                        match_n = int(num)
                        progress_flag = True

        if progress_flag:
            pre_match = match_n - 1

            if pre_match >= 1:
                result_dict = tl.getResults('{}results.log'.format(tournament_log_dir))

                if dbx_flag:
                    for dir_n in conf['log_dir'].split('/'):
                        if 'group' in dir_n:
                            group = dir_n
                    match_dir = tournament_log_dir + '/match_' + str(pre_match)
                    db_match_dir = DROPBOX_BOOT_DIR + '/' + group + '/match_' + str(pre_match)
                    db = tl.MyDropbox(DROPBOX_ACCESS_TOKEN, db_match_dir)
                    db.createFolder(db_match_dir)
                    for match_file in os.listdir(match_dir):
                        # if os.path.getsize( match_dir + '/' + match_file ) != 0:
                        with open(match_dir + '/' + match_file, 'rb') as m_f:
                            f_body = m_f.read()
                        db.uploadFiles(f_body, match_file)
                    db_link = db.get_shared_link(db_match_dir)

                if google_drive_flag:
                    gdrive = tl.MyGoogleDrive()
                    gdrive.upload(LOG_DIR)

                msg = 'match end\n' + tl.getMatchResultMessage(match_dict, result_dict, pre_match)
                if dbx_flag:
                    msg += '\n' + db_link
                if google_drive_flag:
                    msg += '\n https://drive.google.com/drive/folders/{}'.format(GOOGLE_DRIVE_FOLDER_ID)

                tl.sendMessageToChannels(message=message,
                                         message_str=msg,
                                         channels=[original_channel_id, announce_channel_id],
                                         default_id=original_channel_id)
                if discordbot_flag:
                    tl.sendMessageToDiscordChannel(msg)

            msg = 'match start\n' + tl.getMatchStartMessage(match_dict, match_n)

            tl.sendMessageToChannels(message=message,
                                     message_str=msg,
                                     channels=[original_channel_id, announce_channel_id],
                                     default_id=original_channel_id)
            if discordbot_flag:
                tl.sendMessageToDiscordChannel(msg)

            progress_flag = False
        sleep(5)

    # send result of the final match
    # TODO: functionize the same process
    result_dict = tl.getResults('{}results.log'.format(tournament_log_dir))

    if dbx_flag:
        for dir_n in conf['log_dir'].split('/'):
            if 'group' in dir_n:
                group = dir_n
        match_dir = tournament_log_dir + '/match_' + str(match_dict['max_match'])
        db_match_dir = DROPBOX_BOOT_DIR + '/' + group + '/match_' + str(match_dict['max_match'])
        db = tl.MyDropbox(DROPBOX_ACCESS_TOKEN, db_match_dir)
        db.createFolder(db_match_dir)
        for match_file in os.listdir(match_dir):
            # if os.path.getsize( match_dir + '/' + match_file ) != 0:
            with open(match_dir + '/' + match_file, 'rb') as m_f:
                f_body = m_f.read()
            db.uploadFiles(f_body, match_file)
        db_link = db.get_shared_link(db_match_dir)

    if google_drive_flag:
        gdrive = tl.MyGoogleDrive()
        gdrive.upload(LOG_DIR)

    msg = 'match end\n' + tl.getMatchResultMessage(match_dict, result_dict, match_dict['max_match'])
    if dbx_flag:
        msg += '\n' + db_link
    if google_drive_flag:
        msg += '\n https://drive.google.com/drive/folders/{}'.format(GOOGLE_DRIVE_FOLDER_ID)

    tl.sendMessageToChannels(message=message,
                             message_str=msg,
                             channels=[original_channel_id, announce_channel_id],
                             default_id=original_channel_id)
    if discordbot_flag:
        tl.sendMessageToDiscordChannel(msg)

    announce_flag = False


@listen_to(r'^check matches \w+')
@in_channel(ORGANIZER_CHANNEL_NAME)
def listen_func(message):
    txt_list = message.body['text'].split()
    group = txt_list[2]
    if len(txt_list) == 3 and 'group' in group:
        if os.path.exists('{}config/group.yml'.format(COMPETITION_MANAGER_PATH)):
            groups_yml = tl.loadYml('{}config/group.yml'.format(COMPETITION_MANAGER_PATH))
            if group in groups_yml.keys():
                teams_in_group = groups_yml[group]
            else:
                msg = '\'{}\' is not exist.\nPlease create groups before using this command.'
                message.reply(msg)
                return
        else:
            msg = 'There is no \'group.yml\'.\nPlease create groups before using this command.'
            message.reply(msg)
            return
    else:
        msg = tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    tmp_setting = {'teams': teams_in_group,
                   'log_dir': 'tmp'}

    # save as tmp yml in order to avoid overwriting the current tournament configuration
    tmp_yml_name = '{}config/check_matches.yml'.format(COMPETITION_MANAGER_PATH)
    tl.overwriteYml(tmp_yml_name, tmp_setting)
    group_match_sim = tl.startSimulate(tmp_yml_name.format(COMPETITION_MANAGER_PATH))
    tmp_yml = tl.loadYml(tmp_yml_name)
    os.remove(tmp_yml_name.format(COMPETITION_MANAGER_PATH))

    print(group_match_sim.stdout)

    matches = group_match_sim.stdout.split("\n")
    msg = ''
    for i in range(len(matches) - 2):
        if i == 0:
            continue
        elif i > 1:
            mod_row = matches[i].split()
            mod_row[1] = mod_row[1].replace(tmp_yml['teams_dir'] + '/', '')
            mod_row[3] = mod_row[3].replace(tmp_yml['teams_dir'] + '/', '')
            matches[i] = " ".join(mod_row)
        msg += matches[i] + '\n'

    original_channel_id = message.body['channel']
    announce_channel_id = tl.getChannelID(message, ANNOUNCE_CHANNEL_NAME)
    tl.sendMessageToChannels(message=message,
                             message_str=msg,
                             channels=[original_channel_id, announce_channel_id],
                             default_id=original_channel_id)
    if discordbot_flag :
        tl.sendMessageToDiscordChannel(msg)


@listen_to(r'^dropbox\w*')
@in_channel(ORGANIZER_CHANNEL_NAME)
def listen_func(message):
    txt_flag = ''
    txt_list = message.body['text'].split()
    if len(txt_list) == 2:
        global dbx_flag
        if txt_list[1] == 'false':
            dbx_flag = False
            message.send('dropbox_flag is changed to false.')
        elif txt_list[1] == 'true':
            dbx_flag = True
            message.send('dropbox_flag is changed to true.')
            db = tl.MyDropbox(DROPBOX_ACCESS_TOKEN, DROPBOX_BOOT_DIR)
            db.createFolder(DROPBOX_BOOT_DIR)
        else:
            txt_flag = 'help'
            message.send('dropbox_flag is ' + str(dbx_flag))
    else:
        txt_flag = 'help'
        message.send('dropbox_flag is ' + str(dbx_flag))
    if txt_flag == 'help':
        message.send('dropbox [true/false]:switching the dropbox_flag')


@listen_to(r'^gdrive\w*')
@in_channel(ORGANIZER_CHANNEL_NAME)
def listen_func(message):
    txt_list = message.body['text'].split()
    if len(txt_list) == 2:
        global google_drive_flag
        if txt_list[1] == 'false':
            google_drive_flag = False
            message.reply('google_drive_flag is changed to false.')
        elif txt_list[1] == 'true':
            google_drive_flag = True
            message.reply('google_drive_flag is changed to true.')
        else:
            msg = tl.getHelpMessageForOrganizers()
            message.reply(msg)
    else:
        msg = tl.getHelpMessageForOrganizers()
        message.reply(msg)


@listen_to(r'^discordbot\w*')
@in_channel(ORGANIZER_CHANNEL_NAME)
def listen_func(message):
    txt_list = message.body['text'].split()
    if len(txt_list) == 2:
        global discordbot_flag
        if txt_list[1] == 'false':
            discordbot_flag = False
            message.reply('discordbot_flag is changed to false.')
        elif txt_list[1] == 'true':
            discordbot_flag = True
            message.reply('discordbot_flag is changed to true.')
        else:
            msg = tl.getHelpMessageForOrganizers()
            message.reply(msg)
    else:
        msg = tl.getHelpMessageForOrganizers()
        message.reply(msg)


@listen_to(r'^status$')
@in_channel(ORGANIZER_CHANNEL_NAME)
def listen_func(message):
    global bin_flag
    global dbx_flag
    global google_drive_flag
    global discordbot_flag
    global game_flag
    global announce_flag

    msg = 'Status:\n' \
          ' -bin_flag: {}\n' \
          ' -dropbox_flag: {}\n' \
          ' -google_drive_flag: {}\n' \
          ' -discordbot flag: {}\n' \
          ' -game_flag: {}\n' \
          ' -announce_flag: {}\n'.format(bin_flag, dbx_flag, google_drive_flag,
                                         discordbot_flag, game_flag, announce_flag)
    message.reply(msg)


@listen_to(r'^upload start$')
@in_channel(ORGANIZER_CHANNEL_NAME)
def listen_func(message):
    global bin_flag

    yml_name = '{}config/qualification_test.yml'.format(COMPETITION_MANAGER_PATH)
    if not os.path.exists(yml_name):
        msg = 'No qualification_test.yml. Please use \'server\', \'host\' and \'group\' commands before use this command.\n'
        msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    bin_flag = True
    print('bin_flag', bin_flag)
    msg = 'binary upload start'
    message.reply(msg)


@listen_to(r'^upload end$')
@in_channel(ORGANIZER_CHANNEL_NAME)
def listen_func(message):
    global bin_flag
    bin_flag = False
    print('bin_flag', bin_flag)

    archived_time = datetime.datetime.now().strftime('%Y%m%d')
    msg = 'binary upload end.\n Current teams will be archived on {}{}'.format(TEAMS_DIR, archived_time)

    # save pre-uploaded binary
    qualified_teams = tl.getQualifiedTeams()
    for q_team in qualified_teams:
        team_path = os.environ['HOME'] + '/' + q_team + '.tar.gz'
        archive_team_dir = '{}{}/'.format(TEAMS_DIR, archived_time)
        os.makedirs(archive_team_dir, exist_ok=True)
        shutil.copy2(team_path, archive_team_dir)

    message.reply(msg)


@listen_to(r'^test\w*')
@in_channel(ORGANIZER_CHANNEL_NAME)
def listen_func(message):
    success = True
    txt_list = message.body['text'].split()
    if len(txt_list) == 2:
        if txt_list[1] == 'all' or txt_list == '*':
            test_teams = tl.getQualifiedTeams()
        else:
            test_teams = txt_list[1].split(',')
            qualified_teams = tl.getQualifiedTeams()
            for team in test_teams:
                if team not in qualified_teams:
                    message.reply(team + ' is not in qualifications.')
                    success = False
    else:
        success = False

    if not success:
        msg = tl.getHelpMessageForOrganizers()
        message.send(msg)
        return

    global game_flag
    if game_flag:
        message.send('a game is conducted now.')
        return

    game_flag = True

    global stop_flag
    stop_flag = False

    for t_team in test_teams:
        if stop_flag:
            message.reply("cancel test")
            break

        time = datetime.datetime.now().strftime('%Y%m%d%H%M')
        yml_name = '{}config/qualification_test.yml'.format(COMPETITION_MANAGER_PATH)
        log_dir = "log/" + t_team + '/' + time

        conf = tl.loadYml(yml_name)
        conf['log_dir'] = log_dir
        conf['teams'] = [t_team, 'agent2d']
        tl.overwriteYml('{}config/qualification_test.yml'.format(COMPETITION_MANAGER_PATH), conf)

        message.send(t_team + ' test start')
        _ = tl.startGame(yml_name)
        message.send(t_team + ' test finish')

        # move logfiles to competition-manager
        os.makedirs(LOG_DIR+'test/', exist_ok=True)
        shutil.move('{}{}'.format(TOURNAMENT_PATH, log_dir), '{}test/{}/{}'.format(LOG_DIR, t_team, time))

    message.send('test complete')
    game_flag = False


@listen_to(r'^stop test$')
@in_channel(ORGANIZER_CHANNEL_NAME)
def listen_func(message):
    global stop_flag
    stop_flag = True
    msg = 'stop test'
    message.reply(msg)


@respond_to('^bin \w+')
def file_download(message):
    userid = message.body['user']
    email = message.channel._client.users[userid]['profile']['email']
    teamname = message.body['text']
    teamname = ''.join(teamname[4:])

    original_channel_id = message.body['channel']
    organizer_channel_id = tl.getChannelID(message, ORGANIZER_CHANNEL_NAME)

    global bin_flag
    if not bin_flag:
        msg = 'Binary upload is not allowed now.'
        message.reply(msg)
        return

    list_flag = False
    only_mail_flag = False
    only_team_flag = False
    with open('{}config/maillist.txt'.format(COMPETITION_MANAGER_PATH), mode='rt', encoding='utf-8') as f:
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

    if not list_flag:
        if only_team_flag:
            msg = 'Only the team leader can upload team binary.'
        elif only_mail_flag:
            msg = 'Your team name may be \'{}\', not \'{}\''.format(tmp_team, teamname)
        else:
            msg = 'Your team is not resistered. Please ask organizers.'
        message.reply(msg)
        return

    is_first_comment = False
    global game_flag
    while True:
        if game_flag:
            if not is_first_comment:
                msg = 'Another team is testing now.\n Please wait a moment...'
                message.reply(msg)
                is_first_comment = True
            sleep(10)
        else:
            break

    game_flag = True
    if is_first_comment:
        msg = 'Sorry for late testing. Your binary test starts soon.'
        message.reply(msg)

    # teamdir = os.environ['HOME'] + '/' + teamname
    # temporary place in order to avoid illegal upload
    temporary_dir = COMPETITION_MANAGER_PATH + 'uploaded_team/'
    os.makedirs(temporary_dir, exist_ok=True)

    file_types = ['gzip', 'binary']
    download_file = dl.DownloadFile(file_types, temporary_dir)
    if 'files' in message._body.keys():
        filename = message._body['files'][0]['name']
        result = download_file.exe_download(message._body['files'][0])
    else:
        result = 'empty'

    print("bin download ", result)
    if result == 'ok':
        if teamname != filename.split('.tar.gz')[0]:
            msg = 'Attached file\'s name [{}] is different from your command [{}]'.format(filename.split('.tar.gz')[0], teamname)
            tl.sendMessageToChannels(message=message,
                                     message_str=msg,
                                     channels=[original_channel_id, organizer_channel_id],
                                     default_id=original_channel_id)
            game_flag = False
            return
        msg = 'Binary upload succeeded.'
        tl.sendMessageToChannels(message=message,
                                 message_str=msg,
                                 channels=[original_channel_id, organizer_channel_id],
                                 default_id=original_channel_id)

    elif result == 'file type is not applicable.':
        message.reply('File type is not applicable.\n Applicable file type is tar.gz')
        game_flag = False
        return
    elif result == 'empty':
        message.reply('Attached file is not exist.')
        game_flag = False
        return
    elif result == 'type null':
        message.reply(
            'Uploading binary may be too fast.\n please wait approx. 10 seconds after uploading binary is completed')
        game_flag = False
        return
    else:
        message.send('Uploading file is failed.')
        game_flag = False
        return

    sleep(5)

    extract = subprocess.run(['{}/test/extend.sh'.format(COMPETITION_MANAGER_PATH),
                              filename,
                              temporary_dir,
                              COMPETITION_MANAGER_PATH], encoding='utf-8', stdout=subprocess.PIPE)
    if 'Error is not recoverable' in extract.stdout:
        message.reply("Uploaded file cannot be extracted. Please check the contents of the uploaded file.")
        game_flag = False
        return

    if os.path.isdir(temporary_dir):
        teamfiles = os.listdir('{}{}'.format(temporary_dir, teamname))
        if "start" not in teamfiles:
            message.reply("There is no \'start\' script in your file.")
            game_flag = False
            return
        if "kill" not in teamfiles:
            message.send("There is no \'kill\' script in your file.")
            game_flag = False
            return
        if "team.yml" not in teamfiles:
            ty_dict = {"country": teamname}
            tl.saveYml(ty_dict, '{}{}/team.yml'.format(temporary_dir, teamname))

        for excecuted in teamfiles:
            os.chmod(temporary_dir + teamname + '/' + excecuted, 0o777)
    else:
        message.reply(
            "The structure of team directory is wrong or the name of team directory is different from \'{}\'".format(teamname)
        )
        game_flag = False
        return

    shutil.copy2('{}{}.tar.gz'.format(temporary_dir, teamname), os.environ['HOME'])
    copy_tree('{}{}'.format(temporary_dir, teamname), '{}/{}'.format(os.environ['HOME'], teamname))
    os.remove('{}{}.tar.gz'.format(temporary_dir, teamname))

    message.reply('Binary test start (please wait approx. 2 min.)')

    upload_time= datetime.datetime.now().strftime('%Y%m%d%H%M')
    yml_name = '{}config/qualification_test.yml'.format(COMPETITION_MANAGER_PATH)
    log_dir = "log/" + teamname + "/" + upload_time

    tournament_conf = tl.loadYml(yml_name)

    # update qualification_test.yml
    tournament_conf['log_dir'] = log_dir
    tournament_conf['teams_dir'] = os.environ['HOME']
    tournament_conf['teams'] = [teamname, 'agent2d']
    tournament_conf['server_conf'] = 'config/rcssserver/server_test.conf'
    tl.overwriteYml(yml_name, tournament_conf)

    result_game = tl.startGame(yml_name)
    print(result_game.stdout)

    # analyze the test
    result_analyze = subprocess.run(['{}/test/analyze_test.sh'.format(COMPETITION_MANAGER_PATH),
                                     TOURNAMENT_PATH + log_dir, LOGANALYZER_PATH],
                                     encoding='utf-8', stdout=subprocess.PIPE)
    print(result_analyze.stdout)

    if os.path.exists(TOURNAMENT_PATH + log_dir + '/match_1'):
        for f_name in os.listdir(TOURNAMENT_PATH + log_dir + '/match_1'):
            if 'rc' in f_name and '.gz' in f_name:
                tl.upload_file_s(TOURNAMENT_PATH + log_dir + '/match_1/' + f_name,
                                 message.body['channel'])

    discon_index = result_analyze.stdout.find('DisconnectedPlayer')
    discon_p = result_analyze.stdout[discon_index + len('DisconnectedPlayer'):].replace('\n', '')
    print('discon_p', discon_p)

    # save the succeeded team_name to qualification.txt
    try:
        if discon_p != '' and int(discon_p) == 0:
            if os.path.exists('{}config/qualification.txt'.format(COMPETITION_MANAGER_PATH)):
                qualified_team = tl.getQualifiedTeams()
                if teamname not in qualified_team:
                    with open('{}config/qualification.txt'.format(COMPETITION_MANAGER_PATH), 'a+') as q_txt_ad:
                        q_txt_ad.writelines(teamname + ',' + upload_time + '\n')
                else:
                    # already qualified. update the last uploaded time
                    mod_q = []
                    for line in qualified_team:
                        if teamname in line:
                            tmp_line = teamname + ',' + upload_time + '\n'
                            mod_q.append(tmp_line)
                        else:
                            mod_q.append(line)
                    with open('{}config/qualification.txt'.format(COMPETITION_MANAGER_PATH), 'w') as q_txt_ad:
                        q_txt_ad.writelines(mod_q)
            else:
                with open('{}config/qualification.txt'.format(COMPETITION_MANAGER_PATH), 'w') as q_txt:
                    q_txt.writelines(teamname + ',' + upload_time + '\n')

            # success message
            msg = '{}:Binary test succeeded.'.format(teamname)
            tl.sendMessageToChannels(message=message,
                                     message_str=msg,
                                     channels=[original_channel_id, organizer_channel_id],
                                     default_id=original_channel_id)
            msg = 'Please check that your team worked correctly.'
            message.send(msg)

        elif discon_p != '' and int(discon_p) > 0:
            # something error message
            message.send('The number of disconnected players is {}. The connection with rcssserver was successful, '
                         'but team binary has something error.'.format(discon_p))
        else:
            message.send('??? Something wrong ???')
    except Exception:
        # failed message
        msg = '{}:Binary test failed.'.format(teamname)
        tl.sendMessageToChannels(message=message,
                                 message_str=msg,
                                 channels=[original_channel_id, organizer_channel_id],
                                 default_id=original_channel_id)

    # move logfiles to competition-manager
    os.makedirs(LOG_DIR+'test/', exist_ok=True)
    shutil.move('{}{}'.format(TOURNAMENT_PATH, log_dir), '{}test/{}/{}'.format(LOG_DIR, teamname, upload_time))

    # reset game flag
    game_flag = False


@listen_to('^clear$')
@in_channel(ORGANIZER_CHANNEL_NAME)
def file_download(message):
    qualification_path = '{}config/qualification.txt'.format(COMPETITION_MANAGER_PATH)
    if os.path.exists(qualification_path):
        with open(qualification_path, 'w') as _:
            pass

    maillist_path = '{}config/maillist.txt'.format(COMPETITION_MANAGER_PATH)
    if os.path.exists(maillist_path):
        with open(maillist_path, 'w') as m_txt:
            m_txt.write('hogehoge@gmail.com,teamname1\nfugafuga@gmail.com,teamname2\n')

    message.reply('setting files are cleared.')


@listen_to('^register \S+$')
@in_channel(ORGANIZER_CHANNEL_NAME)
def register_team(message):
    body_txt = message.body['text']
    splitted_body_txt = body_txt.split()[-1].split(',')

    if len(splitted_body_txt) != 2:
        msg = tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    # remove link
    if '<mailto:' in splitted_body_txt[0]:
        splitted_body_txt[0] = splitted_body_txt[0].split('|')[-1].replace('>', '')

    maillist_path = '{}config/maillist.txt'.format(COMPETITION_MANAGER_PATH)
    with open(maillist_path, 'a') as m_txt:
        m_txt.write(','.join(splitted_body_txt)+'\n')
    message.reply('{},{} are registered in maillist.txt'.format(splitted_body_txt[0], splitted_body_txt[1]))


@listen_to('^share \w+$')
@in_channel(ORGANIZER_CHANNEL_NAME)
def file_upload(message):
    if not google_drive_flag:
        msg = 'google_drive flag is False. Please use after google_drive_flag True by using \'gdrive\' command.'
        message.reply(msg)

    txt = message.body['text'].split()
    if len(txt) != 2 or (txt[-1] != 'logs' and txt[-1] != 'teams'):
        msg = tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    gdrive = tl.MyGoogleDrive()
    upload_target = LOG_DIR if txt[-1] == 'logs' else TEAMS_DIR
    gdrive.upload(upload_target)

    msg = 'upload to https://drive.google.com/drive/folders/{}'.format(GOOGLE_DRIVE_FOLDER_ID)

    original_channel_id = message.body['channel']
    announce_channel_id = tl.getChannelID(message, ANNOUNCE_CHANNEL_NAME)

    tl.sendMessageToChannels(message=message,
                             message_str=msg,
                             channels=[original_channel_id, announce_channel_id],
                             default_id=original_channel_id)
    if discordbot_flag:
        tl.sendMessageToDiscordChannel(message_str=msg)
