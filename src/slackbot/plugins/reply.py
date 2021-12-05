# coding: utf-8
import datetime
import glob
import os
import subprocess
import shutil
import time
from distutils.dir_util import copy_tree
from slackbot.bot import respond_to
from slackbot.bot import listen_to
from plugins.utils import in_channel
from slackbot_settings import *
from plugins import tools as tl
from plugins import bin_download as dl

from time import sleep

bin_flag = False
bin_test_queue = []
dbx_flag = False
google_drive_flag = False
discordbot_flag = False
announcement_channel_status = {}  # the assigned group name will be appended
current_server_status = {}  # the server's ip-address and the assigned group-name will be appended
recovery_mode = False
abort_process = False

if dbx_flag:
    db = tl.MyDropbox(DROPBOX_ACCESS_TOKEN, DROPBOX_BOOT_DIR)
    db.createFolder(DROPBOX_BOOT_DIR)

if os.environ.get("PATH"):
    os.environ["PATH"] = LOGANALYZER_PATH + ":" + os.environ["PATH"]
else:
    os.environ["PATH"] = LOGANALYZER_PATH


@listen_to(r'^help$')
def get_help(message):
    channel_name = message.channel._body['name']
    if channel_name == ORGANIZER_CHANNEL_NAME:
        msg = tl.getHelpMessageForOrganizers()
    elif channel_name == ANNOUNCE_CHANNEL_NAME:
        msg = tl.getHelpMessageForAnnounce()
    else:
        msg = tl.getHelpMessageUnsupported()
    message.reply(msg)


@respond_to(r'^help$')
def get_help(message):
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
def get_team(message):
    msg = 'Qualified teams:\n'
    q_teams_list = tl.getQualifiedTeams()
    for i in range(len(q_teams_list)):
        msg = msg + str(i + 1) + ' : ' + q_teams_list[i] + '\n'
    message.reply(msg)


@listen_to(r'^group\w*')
@in_channel(ORGANIZER_CHANNEL_NAME)
def set_group(message):
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
        if setGroup(message, group=setting[0], team_list=team_list):
            message.reply('{} is saved'.format(setting[0]))
        else:
            message.reply('{}-update failed.'.format(setting[0]))


def setGroup(message, group, team_list):
    qualified_teams = tl.getQualifiedTeams()

    for team in team_list:
        if team not in qualified_teams:
            message.reply('{} is not a qualified team. Cannot register {} in {}'.format(team, team, group))
            team_list.remove(team)

    if len(team_list) >= 2:
        if os.path.exists('{}config/group.yml'.format(COMPETITION_MANAGER_PATH)):
            group_yaml = tl.loadYml('{}config/group.yml'.format(COMPETITION_MANAGER_PATH))
            group_yaml[group] = team_list
        else:
            group_yaml = {group: team_list}
        tl.saveYml(group_yaml, '{}config/group.yml'.format(COMPETITION_MANAGER_PATH))
        tl.overwriteYml('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH), {"teams": team_list})
        tl.overwriteYml('{}config/qualification_test.yml'.format(COMPETITION_MANAGER_PATH), {"teams": team_list})
        return True
    else:
        msg = 'The number of registered teams must be 2 or more than 2.'
        message.reply(msg)
        return False


@listen_to(r'^hosts*')
@in_channel(ORGANIZER_CHANNEL_NAME)
def set_host(message):
    setting = message.body['text'].split()
    if len(setting) == 1:
        if setting[0] == 'hosts':
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
            msg = '{}config/tournament.yml is not exist. Please set hosts by \'host\' command (e.g. hosts 127.0.0.1,127.0.0.1)\n'.format(
                COMPETITION_MANAGER_PATH)
            msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    elif ans_flag == 'set':
        host_list = setting[1].split(',')
        if setHosts(message, host_list):
            message.reply('hosts are updated')
        else:
            message.reply('host-update failed')


def setHosts(message, host_list):
    if len(host_list) % 2 == 0:
        host_yaml = {'hosts': host_list}
        tl.overwriteYml('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH), host_yaml)
        tl.overwriteYml('{}config/qualification_test.yml'.format(COMPETITION_MANAGER_PATH), host_yaml)
        return True
    else:
        msg = 'The number of hosts must be an even number'
        message.reply(msg)
        return False


@listen_to(r'^server*')
@in_channel(ORGANIZER_CHANNEL_NAME)
def set_server(message):
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
            msg = '{}config/tournament.yml does not exist. Please set server by \'server\' command (e.g. server 127.0.0.1)\n'.format(
                COMPETITION_MANAGER_PATH)
            msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    elif ans_flag == 'set':
        server = setting[1]
        if setServer(message, server):
            message.reply('server is updated')
        else:
            message.reply('server-update failed')


def setServer(_, server):
    server_yaml = {'server': server}
    tl.overwriteYml('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH), server_yaml)
    tl.overwriteYml('{}config/qualification_test.yml'.format(COMPETITION_MANAGER_PATH), server_yaml)
    return True


@listen_to(r'^channel*')
@in_channel(ORGANIZER_CHANNEL_NAME)
def set_channel(message):
    setting = message.body['text'].split()
    if len(setting) == 1:
        if setting[0] == 'channel':
            ans_flag = 'status'
        else:
            ans_flag = 'help'
    elif len(setting) == 2:
        if len(setting[1].split(',')) != 2:
            ans_flag = 'status'
        else:
            ans_flag = 'set'
    else:
        ans_flag = 'help'

    if ans_flag == 'help':
        message.reply(tl.getHelpMessageForOrganizers())
        return
    elif ans_flag == 'status':
        if os.path.exists('{}config/channel.yml'.format(COMPETITION_MANAGER_PATH)):
            channel_yml = tl.loadYml('{}config/channel.yml'.format(COMPETITION_MANAGER_PATH))
            if len(setting) == 1:
                msg = 'channel\n'
                for key, value in channel_yml.items():
                    msg += ' -{}: {}\n'.format(key, value)
            else:
                if setting[1] in channel_yml.keys():
                    msg = 'channel of {}\n-{}'.format(setting[1], channel_yml[setting[1]])
                else:
                    msg = 'channel of {} is not assined.'.format(setting[1])
        else:
            msg = '{}config/channel.yml does not exist. Please setup channel by \'channel\'' \
                  ' command (e.g. channel groupA main_tournament_channel)\n'.format(COMPETITION_MANAGER_PATH)
            msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    elif ans_flag == 'set':
        group = setting[1].split(',')[0]
        channel = setting[1].split(',')[1]
        if setChannel(message, group, channel):
            message.reply('channel is updated')
        else:
            message.reply('channel-update failed')


def setChannel(message, group, channel):
    if channel not in ANNOUNCE_CHANNEL_NAME.keys():
        msg = 'Cannot set \'{}\' as the announcement channel. You can choose the channel from the following channel-list' \
              ' (defined in config/manager.yml)\n'.format(channel)
        msg += ','.join(ANNOUNCE_CHANNEL_NAME.keys())
        message.reply(msg)
        return False
    if os.path.exists('{}config/channel.yml'.format(COMPETITION_MANAGER_PATH)):
        channel_yml = tl.loadYml('{}config/channel.yml'.format(COMPETITION_MANAGER_PATH))
        channel_yml[group] = channel
    else:
        channel_yml = {group: channel}
    tl.saveYml(channel_yml, '{}config/channel.yml'.format(COMPETITION_MANAGER_PATH))
    return True


@listen_to(r'^roundrobin title*')
@in_channel(ORGANIZER_CHANNEL_NAME)
def set_roundrobin_title(message):
    setting = message.body['text'].split()
    if len(setting) == 2:
        if setting[0] == 'roundrobin' and setting[1] == 'title':
            ans_flag = 'status'
        else:
            ans_flag = 'help'
    elif len(setting) == 3:
        ans_flag = 'set'
    else:
        ans_flag = 'help'

    if ans_flag == 'help':
        message.reply(tl.getHelpMessageForOrganizers())
        return
    elif ans_flag == 'status':
        if not os.path.exists('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH)):
            msg = 'No tournament.yml. Please use \'server\', \'host\' and \'group\' commands before use this command.\n'
            msg += tl.getHelpMessageForOrganizers()
        else:
            conf = tl.loadYml('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH))
            msg = 'roundrobin title\n-' + conf["title"]
        message.reply(msg)
        return
    elif ans_flag == 'set':
        roundrobin_title = setting[2]
        if setRoundRobinTitle(message, roundrobin_title):
            message.reply('roundrobin_title is updated')
        else:
            message.reply('roundrobin_title-update failed')


def setRoundRobinTitle(_, roundrobin_title):
    roundrobin_dict = {'title': '{}/{}'.format(COMPETITION_NAME, roundrobin_title)}
    tl.overwriteYml('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH), roundrobin_dict)
    tl.overwriteYml('{}config/qualification_test.yml'.format(COMPETITION_MANAGER_PATH), roundrobin_dict)
    return True


@listen_to(r'^conf*')
@in_channel(ORGANIZER_CHANNEL_NAME)
def set_conf(message):
    body_text = message.body['text'].split()
    if len(body_text) == 1:
        ans_flag = 'status'
    elif len(body_text) > 2:
        ans_flag = 'help'
    else:
        ans_flag = 'set'

    if ans_flag == 'help':
        msg = tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return
    elif ans_flag == 'status':
        if not os.path.exists('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH)):
            msg = 'No tournament.yml. Please set tournament parameters by some commands before use this command.\n'
            msg += tl.getHelpMessageForOrganizers()
        else:
            conf = tl.loadYml('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH))
            msg = 'RcssServer config\n-' + conf["server_conf"]
        message.reply(msg)
        return
    else:
        server_conf = body_text[1]
        if setServerConf(message, server_conf):
            message.reply('server_conf is updated')
        else:
            message.reply('server_conf-update failed')


def setServerConf(message, server_conf):
    available_server_conf_list = glob.glob('{}config/rcssserver/server_*.conf'.format(TOURNAMENT_PATH))
    available_server_conf_list = [c.split('/')[-1] for c in available_server_conf_list]
    if server_conf not in available_server_conf_list:
        msg = 'Cannot select {} as a server_conf.\n'.format(server_conf)
        msg += 'You can select the server_conf from the following list\n'
        for c in available_server_conf_list:
            msg += ' -{}\n'.format(c)
        message.reply(msg)
        return False
    else:
        server_conf_dict = {'server_conf': 'config/rcssserver/{}'.format(server_conf)}
        tl.overwriteYml('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH), server_conf_dict)
        tl.overwriteYml('{}config/qualification_test.yml'.format(COMPETITION_MANAGER_PATH), server_conf_dict)
        return True


@listen_to(r'^mode*')
@in_channel(ORGANIZER_CHANNEL_NAME)
def set_mode(message):
    body_text = message.body['text'].split()
    if len(body_text) == 1:
        ans_flag = 'status'
    elif len(body_text) > 2:
        ans_flag = 'help'
    else:
        ans_flag = 'set'

    if ans_flag == 'help':
        msg = tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return
    elif ans_flag == 'status':
        if not os.path.exists('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH)):
            msg = 'No tournament.yml. Please set tournament parameters by some commands before use this command.\n'
            msg += tl.getHelpMessageForOrganizers()
        else:
            conf = tl.loadYml('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH))
            msg = 'Game mode\n-' + conf["mode"]
        message.reply(msg)
        return
    else:
        game_mode = body_text[1]
        if setGameMode(message, game_mode):
            message.reply('game_mode is updated')
        else:
            message.reply('game_mode-update failed')


def setGameMode(message, game_mode):
    available_game_mode_list = ['group', 'one_vs_all', 'single_match']
    if game_mode not in available_game_mode_list:
        msg = 'Cannot select game_mode:{}.\n'.format(game_mode)
        msg += 'You can select the game_mode from the following list\n'
        for g in available_game_mode_list:
            msg += ' -{}\n'.format(g)
        message.reply(msg)
        return False
    else:
        game_mode_dict = {'mode': game_mode}
        tl.overwriteYml('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH), game_mode_dict)
        tl.overwriteYml('{}config/qualification_test.yml'.format(COMPETITION_MANAGER_PATH), game_mode_dict)
        return True


@listen_to(r'^set .+$')
@in_channel(ORGANIZER_CHANNEL_NAME)
def set_all(message):
    body_text = message.body['text'].split()
    # set groupA --teams=teamA,teamB,teamC --server=serverIP --hosts=Host1IP,Host2IP --mode=gameMode --server-conf=serverConf --roundrobin-title=roundrobinTitle --channel=announcementChannelName
    # set groupA -t=teamA,teamB,teamC -s=serverIP -h=Host1IP,Host2IP -m=gameMode -sc=serverConf -rt=roundrobinTitle -c=announcementChannelName
    if len(body_text) < 2:
        msg = tl.getHelpMessageForOrganizers()
        message.reply(msg)

    group = body_text[1]
    for option in body_text:
        if "--teams=" in option or "-t=" in option:
            parser = option.split("=")[-1]
            teams = parser.split(",")
            if setGroup(message, group, teams):
                message.reply('(set) {} is saved'.format(group))
            else:
                message.reply('(set) {}-update failed.'.format(group))
                return
        elif "--server=" in option or "-s=" in option:
            server = option.split("=")[-1]
            if setServer(message, server):
                message.reply('(set) server is updated')
            else:
                message.reply('(set) server-update failed')
                return
        elif "--hosts=" in option or "-h=" in option:
            parser = option.split("=")[-1]
            hosts = parser.split(",")
            if setHosts(message, hosts):
                message.reply('(set) hosts are updated')
            else:
                message.reply('(set) host-update failed')
                return
        elif "--mode=" in option or "-m=" in option:
            game_mode = option.split("=")[-1]
            if setGameMode(message, game_mode):
                message.reply('(set) game-mode is updated')
            else:
                message.reply('(set) game-mode-update failed')
                return
        elif "--server-conf=" in option or "-sc=" in option:
            server_conf = option.split("=")[-1]
            if setServerConf(message, server_conf):
                message.reply('(set) server-conf is updated')
            else:
                message.reply('(set) server-conf-update failed')
                return
        elif "--roundrobin-title=" in option or "-rt=" in option:
            roundrobin_title = option.split("=")[-1]
            if setRoundRobinTitle(message, roundrobin_title):
                message.reply('(set) roundrobin-title is updated')
            else:
                message.reply('(set) roundrobin-title-update failed')
                return
        elif "--channel=" in option or "-c=" in option:
            channel = option.split("=")[-1]
            if setChannel(message, group, channel):
                message.reply('(set) channel is updated')
            else:
                message.reply('(set) channel update failed')
                return
        elif "--" in option and "=" in option:
            message.reply("(set) unknown option {}".format(option.split("=")[0]))

    message.reply('set completed. please check the updated setting by \'setting\' command.')


@listen_to(r'^start \w+')
@in_channel(ORGANIZER_CHANNEL_NAME)
def start_func(message):
    if not os.path.exists('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH)):
        message.reply('{}config/tournament.yml does not exist. Please setup tournament settings by '
                      '\'server\' and \'host\' commands before using this command'.format(COMPETITION_MANAGER_PATH))
        return
    if not os.path.exists('{}config/channel.yml'.format(COMPETITION_MANAGER_PATH)):
        message.reply('{}config/channel.yml does not exist. Please setup channel setting by \'channel\' command before using this command'.format(COMPETITION_MANAGER_PATH))
        return
    channel_conf = tl.loadYml('{}config/channel.yml'.format(COMPETITION_MANAGER_PATH))

    # check game server availability
    tournament_conf = tl.loadYml('{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH))
    target_server_ip = tournament_conf['server']
    global current_server_status
    if target_server_ip in current_server_status.keys():
        message.reply('a game is conducted now at {} (tournament:{}).'.format(target_server_ip,
                                                                              current_server_status[target_server_ip]))
        return

    if bin_flag:
        message.reply('Binary upload must be prohibit by the command \'binary upload end\'.')
        return

    txt_list = message.body['text'].split()

    if len(txt_list) != 2:
        message.reply(tl.getHelpMessageForOrganizers())
        return

    group = txt_list[-1]
    dt_start = datetime.datetime.now().strftime('%Y%m%d%H%M')

    teams = tl.getTeamsInGroup(group)
    if len(teams) == 0:
        msg = '\'{}\' is empty. Please create groups by \'group\' command before using this command.'.format(group)
        message.reply(msg)
        return
    for ipaddress, executing_group in current_server_status.items():
        if executing_group == group:
            msg = '\'{}\' is conducted at {}'.format(group, ipaddress)
            message.reply(msg)
            return
    if os.path.exists('{}{}/{}'.format(LOG_DIR, tournament_conf['title'], group)):
        msg = '\'{}\' is already finished'.format(group)
        message.reply(msg)
        return
    if group not in channel_conf.keys():
        msg = 'Channel that announce the result of {} is not set yet. Please setup it by \'channel\' command'.format(group)
        message.reply(msg)
        return

    tournament_conf['log_dir'] = '{}/{}'.format(dt_start, group)
    tl.overwriteYml('{}config/tournament_{}.yml'.format(COMPETITION_MANAGER_PATH, group), tournament_conf)

    # set current server status
    current_server_status[target_server_ip] = group

    conf = tl.loadYml('{}config/tournament_{}.yml'.format(COMPETITION_MANAGER_PATH, group))

    qualified_dir = "{}qualified_team/".format(COMPETITION_MANAGER_PATH)

    print('sync tournament scripts and teams...')
    tl.rsync(TOURNAMENT_PATH.rstrip('/'), '{}:/home/{}'.format(conf['server'], USERNAME))
    tl.rsync('{}config/tournament_{}.yml'.format(COMPETITION_MANAGER_PATH, group),
             '{}:/home/{}/tournament/config/tournament.yml'.format(conf['server'], USERNAME))
    for teamname in conf['teams']:
        # sync teams to server
        tl.rsync('{}{}'.format(qualified_dir, teamname), '{}:/home/{}'.format(conf['server'], USERNAME), delete=True)
        for h in conf['hosts']:
            if h == conf['server']:
                continue
            # sync teams to server
            tl.rsync('{}/{}'.format(qualified_dir, teamname), '{}:/home/{}'.format(h, USERNAME), delete=True)

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

    if conf['mode'] == 'group' or conf['mode'] == 'one_vs_all':
        # simulate
        msg = tl.getGroupMatchListMessage(group, tournament_conf)
        # msg = group + ' tournament starts soon \n' \
        #  'Start time : ' + dt_start + '\nI will notify you when all games are finished.\n'

        message.react('+1')
        original_channel_id = message.body['channel']
        slack_announce_channel_id = tl.getChannelID(message, ANNOUNCE_CHANNEL_NAME[channel_conf[group]]['slack'])
        discord_announce_channel_id = ANNOUNCE_CHANNEL_NAME[channel_conf[group]]['discord']
        tl.sendMessageToChannels(message=message,
                                 message_str=msg,
                                 channels=[original_channel_id, slack_announce_channel_id],
                                 default_id=original_channel_id)
        if discordbot_flag:
            tl.sendMessageToDiscordChannel(msg, discord_announce_channel_id)

        # save match list
        match_dict = {}
        max_match = 0

        for match_line in msg.split('\n'):
            if 'vs' in match_line:
                splitted_match_line = match_line.split()
                match_name = 'match_' + splitted_match_line[0].rstrip(':')
                match_team = {}
                match_team['team_l'] = splitted_match_line[1]
                match_team['team_r'] = splitted_match_line[3]
                match_dict[match_name] = match_team
                max_match = max(max_match, int(splitted_match_line[0].rstrip(':')))
        match_dict['max_match'] = max_match
        tl.saveYml(match_dict, '{}config/match_list_{}.yml'.format(COMPETITION_MANAGER_PATH, group))

        # start game
        _ = tl.startGame(conf['server'],
                         '/home/{}/tournament/config/tournament.yml'.format(USERNAME))

        aborted = False
        global abort_process
        while abort_process:
            if not aborted:
                aborted = True
            time.sleep(3)

        # sync game logs to slackserver
        tl.rsync('{}:/home/{}/tournament/{}'.format(conf['server'], USERNAME, dt_start),
                 TOURNAMENT_PATH.rstrip('/'))
        # remove game logs in rcssserver
        tl.cmdAtRemoteServer(conf['server'],
                             'rm -r /home/{}/tournament/{}'.format(USERNAME, dt_start))

    else:
        msg = 'Illegal game mode \'{}\'.'.format(conf['mode'])
        message.reply(msg)
        return

    msg = group + ' tournament is over.\n' if not aborted else group + ' tournament is aborted. \n'

    if dbx_flag:
        db_g_link = db.get_shared_link(DROPBOX_BOOT_DIR + '/' + group)
        msg += '\n' + db_g_link

    if google_drive_flag:
        msg += '\n logs are available here. https://drive.google.com/drive/folders/{}'.format(GOOGLE_DRIVE_FOLDER_ID)

    current_server_status.pop(target_server_ip)

    # wait for finishing announce
    while True:
        if group not in announcement_channel_status.keys():
            break

    # check the aborted match
    if aborted:
        matches_list = glob.glob('{}{}/match_*'.format(TOURNAMENT_PATH, conf['log_dir']))
        for match in matches_list:
            match_name = match.split('/')[-1]
            files_list = glob.glob('{}{}/{}/*.rc*.gz'.format(TOURNAMENT_PATH, conf['log_dir'], match_name))
            if len(files_list) != 2:
                shutil.rmtree('{}{}/{}'.format(TOURNAMENT_PATH, conf['log_dir'], match_name))
        # remove the aborted log files
        _ = tl.cmdAtRemoteServer(conf['server'], 'rm /home/{}/tournament/*.rc*.gz'.format(USERNAME))

    # copy the game log files
    os.makedirs('{}{}'.format(LOG_DIR, conf['title']), exist_ok=True)
    copy_tree('{}{}'.format(TOURNAMENT_PATH, dt_start), '{}{}'.format(LOG_DIR, conf['title']))
    os.makedirs('{}{}'.format(LOG_DIR, 'archive/'), exist_ok=True)
    shutil.move('{}{}'.format(TOURNAMENT_PATH, dt_start), '{}archive'.format(LOG_DIR))

    tl.sendMessageToChannels(message=message,
                             message_str=msg,
                             channels=[original_channel_id, slack_announce_channel_id],
                             default_id=original_channel_id)
    if discordbot_flag:
        tl.sendMessageToDiscordChannel(msg, discord_announce_channel_id)


@listen_to(r'^announce match .+$')
@in_channel(ORGANIZER_CHANNEL_NAME)
def announce_func(message):
    body_text = message.body['text'].split()
    if len(body_text) != 3:
        msg = 'Illegal input.\n'
        msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    group = body_text[2]

    if not os.path.exists('{}config/tournament_{}.yml'.format(COMPETITION_MANAGER_PATH, group)):
        msg = 'No tournament_{}.yml. Please start a tournament by \'start\' commands before use this command.\n'
        msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    if not os.path.exists('{}config/channel.yml'.format(COMPETITION_MANAGER_PATH)):
        message.reply('{}config/channel.yml does not exist. Please setup channel setting by \'channel\' '
                      'command before using this command'.format(COMPETITION_MANAGER_PATH))
        return

    channel_conf = tl.loadYml('{}config/channel.yml'.format(COMPETITION_MANAGER_PATH))

    if group not in channel_conf.keys():
        msg = 'Channel that announce the result of {} is not set yet. Please setup it by \'channel\' command'.format(group)
        message.reply(msg)
        return

    conf = tl.loadYml('{}config/tournament_{}.yml'.format(COMPETITION_MANAGER_PATH, group))
    target_server_ip = conf['server']
    tournament_log_dir = '{}{}/'.format(TOURNAMENT_PATH, conf['log_dir'])
    match_dict = tl.loadYml('{}config/match_list_{}.yml'.format(COMPETITION_MANAGER_PATH, group))
    dt_start = conf['log_dir'].split('/')[0]

    match_n = 0

    original_channel_id = message.body['channel']
    slack_announce_channel_id = tl.getChannelID(message, ANNOUNCE_CHANNEL_NAME[channel_conf[group]]['slack'])
    discord_announce_channel_id = ANNOUNCE_CHANNEL_NAME[channel_conf[group]]['discord']

    progress_flag = False
    global announcement_channel_status
    announcement_channel_status[group] = channel_conf[group]
    global current_server_status
    while target_server_ip in current_server_status.keys():
        # sync game logs (remove the previous one)
        tl.rsync('{}:/home/{}/tournament/{}'.format(conf['server'], USERNAME, dt_start),
                 TOURNAMENT_PATH.rstrip('/'))

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

                group = conf['log_dir'].split('/')[-1]
                match_dir = 'match_' + str(pre_match)

                if not os.path.exists(tournament_log_dir + match_dir):
                    continue

                if dbx_flag:
                    tournament_match_dir = tournament_log_dir + match_dir
                    db_match_dir = DROPBOX_BOOT_DIR + '/' + group + '/' + match_dir
                    db = tl.MyDropbox(DROPBOX_ACCESS_TOKEN, db_match_dir)
                    db.createFolder(db_match_dir)
                    for match_file in os.listdir(tournament_match_dir):
                        # if os.path.getsize( match_dir + '/' + match_file ) != 0:
                        with open(tournament_match_dir + '/' + match_file, 'rb') as m_f:
                            f_body = m_f.read()
                        db.uploadFiles(f_body, match_file)
                    db_link = db.get_shared_link(db_match_dir)

                if google_drive_flag:
                    gdrive = tl.MyGoogleDrive()
                    gdrive.upload(tournament_log_dir + match_dir, prefix='logs/{}/{}'.format(conf['title'], group))

                msg = 'The game finished with the following scores:\n' + tl.getMatchResultMessage(match_dict,
                                                                                                  result_dict,
                                                                                                  pre_match)
                if dbx_flag:
                    msg += '\n' + db_link
                if google_drive_flag:
                    msg += '\n https://drive.google.com/drive/folders/{}'.format(GOOGLE_DRIVE_FOLDER_ID)

                tl.sendMessageToChannels(message=message,
                                         message_str=msg,
                                         channels=[original_channel_id, slack_announce_channel_id],
                                         default_id=original_channel_id)
                if discordbot_flag:
                    tl.sendMessageToDiscordChannel(msg, discord_announce_channel_id)

            msg = 'The following game has started:\n' + tl.getMatchStartMessage(match_dict, match_n)

            tl.sendMessageToChannels(message=message,
                                     message_str=msg,
                                     channels=[original_channel_id, slack_announce_channel_id],
                                     default_id=original_channel_id)
            if discordbot_flag:
                tl.sendMessageToDiscordChannel(msg, discord_announce_channel_id)

            progress_flag = False
        sleep(5)

    # send result of the final match
    # TODO: functionize the same process
    result_dict = tl.getResults('{}results.log'.format(tournament_log_dir))

    group = conf['log_dir'].split('/')[-1]
    match_dir = 'match_' + str(match_dict['max_match'])

    if os.path.exists(tournament_log_dir + match_dir):
        if dbx_flag:
            tournament_match_dir = tournament_log_dir + match_dir
            db_match_dir = DROPBOX_BOOT_DIR + '/' + group + '/' + match_dir
            db = tl.MyDropbox(DROPBOX_ACCESS_TOKEN, db_match_dir)
            db.createFolder(db_match_dir)
            for match_file in os.listdir(tournament_match_dir):
                # if os.path.getsize( tournament_match_dir + '/' + match_file ) != 0:
                with open(match_dir + '/' + match_file, 'rb') as m_f:
                    f_body = m_f.read()
                db.uploadFiles(f_body, match_file)
            db_link = db.get_shared_link(db_match_dir)

        if google_drive_flag:
            gdrive = tl.MyGoogleDrive()
            gdrive.upload(tournament_log_dir + match_dir, prefix='logs/{}/{}'.format(conf["title"], group))

        msg = 'The game finished with the following scores:\n' + tl.getMatchResultMessage(match_dict,
                                                                                          result_dict,
                                                                                          match_dict['max_match'])
        if dbx_flag:
            msg += '\n' + db_link
        if google_drive_flag:
            msg += '\n https://drive.google.com/drive/folders/{}'.format(GOOGLE_DRIVE_FOLDER_ID)

        tl.sendMessageToChannels(message=message,
                                 message_str=msg,
                                 channels=[original_channel_id, slack_announce_channel_id],
                                 default_id=original_channel_id)
        if discordbot_flag:
            tl.sendMessageToDiscordChannel(msg, discord_announce_channel_id)

    announcement_channel_status.pop(group)


@listen_to(r'^check matches \w+')
@in_channel(ORGANIZER_CHANNEL_NAME)
def check_matches_func(message):
    txt_list = message.body['text'].split()
    group = txt_list[2]
    if len(txt_list) == 3 and 'group' in group:
        teams = tl.getTeamsInGroup(group)
        if len(teams) == 0:
            msg = '\'{}\' is empty. Please create groups by \'group\' command before using this command.'.format(
                group)
            message.reply(msg)
            return
    else:
        msg = tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    if not os.path.exists('{}config/tournament_{}.yml'.format(COMPETITION_MANAGER_PATH, group)):
        msg = 'No tournament_{}.yml. Please start a tournament by \'start\' commands before use this command.\n'
        msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    tournament_conf = tl.loadYml('{}config/tournament_{}.yml'.format(COMPETITION_MANAGER_PATH, group))
    msg = tl.getGroupMatchListMessage(group, tournament_conf)
    message.reply(msg)


@listen_to(r'^abort \w+$')
@in_channel(ORGANIZER_CHANNEL_NAME)
def abort_func(message):
    body_text = message.body['text'].split()
    if len(body_text) != 2:
        msg = 'Illegal input.\n'
        msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    group = body_text[-1]
    global current_server_status
    if group not in current_server_status.values():
        msg = '{} is not executing now.'.format(group)
        message.reply(msg)
        return

    global abort_process
    abort_process = True

    for key, value in current_server_status.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        if value == group:
            server = key
            break

    tournament_conf = tl.loadYml("{}config/tournament_{}.yml".format(COMPETITION_MANAGER_PATH, group))

    # kill tournament script
    cmd = "ps aux | grep \"[s]sh {} cd tournament; ./start.sh\" | tail -n 1".format(server)
    ssh_process_id = tl.cmdAtLocalhost(cmd).stdout.split()[1]
    msg = 'kill tournament script...'
    print(msg)
    message.reply(msg)
    _ = tl.cmdAtLocalhost('kill {}'.format(ssh_process_id))

    # kill rcssserver
    cmd = 'ps aux | grep [r]cssserver | tail -n 1'.format(server)
    rcssserver_process_id = tl.cmdAtRemoteServer(server, cmd).stdout.split()[1]
    msg = 'kill rcssserver...'
    print(msg)
    message.reply(msg)
    _ = tl.cmdAtRemoteServer(server, 'kill {}'.format(rcssserver_process_id))

    # kill agents
    teams = tournament_conf['teams']
    msg = 'kill agents...'
    print(msg)
    message.reply(msg)
    for t in teams:
        _ = tl.cmdAtRemoteServer(server, '/home/{}/{}/kill'.format(USERNAME, t))
    abort_process = False


@listen_to(r'^resume \w+')
@in_channel(ORGANIZER_CHANNEL_NAME)
def resume_func(message):
    body_text = message.body['text'].split()
    if len(body_text) != 2:
        msg = 'Illegal input.\n'
        msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return
    group = body_text[-1]

    if not os.path.exists('{}config/tournament_{}.yml'.format(COMPETITION_MANAGER_PATH, group)):
        message.reply('{}config/tournament_{}.yml does not exist. You can use this command to use'.format(COMPETITION_MANAGER_PATH, group))
        return
    if not os.path.exists('{}config/channel.yml'.format(COMPETITION_MANAGER_PATH)):
        message.reply('{}config/channel.yml does not exist. Please setup channel setting by \'channel\' command before using this command'.format(COMPETITION_MANAGER_PATH))
        return

    channel_conf = tl.loadYml('{}config/channel.yml'.format(COMPETITION_MANAGER_PATH))
    # check game server availability
    tournament_conf = tl.loadYml('{}config/tournament_{}.yml'.format(COMPETITION_MANAGER_PATH, group))
    target_server_ip = tournament_conf['server']
    global current_server_status
    if target_server_ip in current_server_status.keys():
        message.reply('a game is conducted now at {} (tournament:{}).'.format(target_server_ip,
                                                                              current_server_status[target_server_ip]))
        return

    if bin_flag:
        message.reply('Binary upload must be prohibit by the command \'binary upload end\'.')
        return

    for ipaddress, executing_group in current_server_status.items():
        if executing_group == group:
            msg = '\'{}\' is conducted at {}'.format(group, ipaddress)
            message.reply(msg)
            return
    if not os.path.exists('{}{}/{}'.format(LOG_DIR, tournament_conf['title'], group)):
        msg = '\'{}\' is not aborted before'.format(group)
        message.reply(msg)
        return
    if group not in channel_conf.keys():
        msg = 'Channel that announce the result of {} is not set yet. Please setup it by \'channel\' command'.format(group)
        message.reply(msg)
        return

    msg = 'Resume {}\n'.format(group)
    msg += tl.getGroupMatchListMessage(group, tournament_conf)

    message.react('+1')
    original_channel_id = message.body['channel']
    slack_announce_channel_id = tl.getChannelID(message, ANNOUNCE_CHANNEL_NAME[channel_conf[group]]['slack'])
    discord_announce_channel_id = ANNOUNCE_CHANNEL_NAME[channel_conf[group]]['discord']
    tl.sendMessageToChannels(message=message,
                             message_str=msg,
                             channels=[original_channel_id, slack_announce_channel_id],
                             default_id=original_channel_id)
    if discordbot_flag:
        tl.sendMessageToDiscordChannel(msg, discord_announce_channel_id)

    # set current server status
    current_server_status[target_server_ip] = group

    # !!! not sync teams under a assumption that teams must be same as the aborted situation !!!
    # !!! if you want to replace a team, you have to do by yourself. !!!
    print('sync tournament scripts...')
    tl.rsync(TOURNAMENT_PATH.rstrip('/'), '{}:/home/{}'.format(tournament_conf['server'], USERNAME))
    tl.rsync('{}config/tournament_{}.yml'.format(COMPETITION_MANAGER_PATH, group),
             '{}:/home/{}/tournament/config/tournament.yml'.format(tournament_conf['server'], USERNAME))

    # sync game logs to rcssserver
    tl.cmdAtRemoteServer(target_server_ip, 'cd tournament; mkdir -p {}'.format(tournament_conf['log_dir']))
    # cannot use rsync the path including spaces
    tl.rsync('\"{}{}/{}\"'.format(LOG_DIR, tournament_conf['title'], group),
             '{}:/home/{}/tournament/{}'.format(target_server_ip, USERNAME, tournament_conf['log_dir'].split('/')[0]))

    # resume game
    a = tl.resumeGame(target_server_ip,
                      '/home/{}/tournament/config/tournament.yml'.format(USERNAME))

    aborted = False
    global abort_process
    while abort_process:
        if not aborted:
            aborted = True
        time.sleep(3)

    # sync game logs to slackserver
    dt_start = tournament_conf['log_dir'].split('/')[0]
    tl.rsync('{}:/home/{}/tournament/{}'.format(target_server_ip, USERNAME, dt_start),
             TOURNAMENT_PATH.rstrip('/'))
    # remove game logs in rcssserver
    tl.cmdAtRemoteServer(target_server_ip,
                         'rm -r /home/{}/tournament/{}'.format(USERNAME, dt_start))

    msg = group + ' tournament is over.\n' if not aborted else group + ' tournament is aborted. \n'

    if dbx_flag:
        db_g_link = db.get_shared_link(DROPBOX_BOOT_DIR + '/' + group)
        msg += '\n' + db_g_link

    if google_drive_flag:
        msg += '\n logs are available here. https://drive.google.com/drive/folders/{}'.format(GOOGLE_DRIVE_FOLDER_ID)

    current_server_status.pop(target_server_ip)

    # wait for finishing announce
    while True:
        if group not in announcement_channel_status.keys():
            break

    if aborted:
        matches_list = glob.glob('{}{}/match_*'.format(TOURNAMENT_PATH, tournament_conf['log_dir']))
        for match in matches_list:
            match_name = match.split('/')[-1]
            files_list = glob.glob('{}{}/{}/*.rc*.gz'.format(TOURNAMENT_PATH, tournament_conf['log_dir'], match_name))
            if len(files_list) != 2:
                shutil.rmtree('{}{}/{}'.format(TOURNAMENT_PATH, tournament_conf['log_dir'], match_name))
        # remove the aborted log files
        _ = tl.cmdAtRemoteServer(tournament_conf['server'], 'rm /home/{}/tournament/*.rc*.gz'.format(USERNAME))

    # copy the game log files
    os.makedirs('{}{}'.format(LOG_DIR, tournament_conf['title']), exist_ok=True)
    copy_tree('{}{}'.format(TOURNAMENT_PATH, dt_start), '{}{}'.format(LOG_DIR, tournament_conf['title']))
    os.makedirs('{}{}'.format(LOG_DIR, 'archive/'), exist_ok=True)
    copy_tree('{}{}'.format(TOURNAMENT_PATH, dt_start), '{}archive/{}'.format(LOG_DIR, dt_start))
    shutil.rmtree('{}{}'.format(TOURNAMENT_PATH, dt_start))

    tl.sendMessageToChannels(message=message,
                             message_str=msg,
                             channels=[original_channel_id, slack_announce_channel_id],
                             default_id=original_channel_id)
    if discordbot_flag:
        tl.sendMessageToDiscordChannel(msg, discord_announce_channel_id)


@listen_to(r'^dropbox\w*')
@in_channel(ORGANIZER_CHANNEL_NAME)
def dropbox_func(message):
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
def google_drive_func(message):
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
def discord_bot_func(message):
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
def get_status(message):
    global bin_flag
    global dbx_flag
    global google_drive_flag
    global discordbot_flag
    global current_server_status
    global announcement_channel_status
    global bin_test_queue

    msg = 'Status:\n' \
          ' -bin_flag: {}\n' \
          ' -dropbox_flag: {}\n' \
          ' -google_drive_flag: {}\n' \
          ' -discordbot flag: {}\n' \
          ' -current_server_status: {}\n' \
          ' -announce_channel_status: {}\n' \
          ' -bin_test_queue: {}\n' \
          ' -recovery_mode: {}'.format(bin_flag,
                                       dbx_flag,
                                       google_drive_flag,
                                       discordbot_flag,
                                       current_server_status,
                                       announcement_channel_status,
                                       ','.join(bin_test_queue),
                                       recovery_mode)
    message.reply(msg)


@listen_to(r'^setting*')
@in_channel(ORGANIZER_CHANNEL_NAME)
def get_setting(message):
    body_txt = message.body['text'].split()
    if len(body_txt) >= 3:
        msg = 'Illegal input.\n'
        msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    if len(body_txt) == 2 and not os.path.exists('{}config/tournament_{}.yml'.format(COMPETITION_MANAGER_PATH, body_txt[1])):
        message.reply('{}config/tournament_{}.yml is not exist.'.format(COMPETITION_MANAGER_PATH, body_txt[1]))
        return

    if len(body_txt) == 1:
        yml_name = '{}config/tournament.yml'.format(COMPETITION_MANAGER_PATH)

    elif len(body_txt) == 2:
        yml_name = '{}config/tournament_{}.yml'.format(COMPETITION_MANAGER_PATH, body_txt[1])

    if not os.path.exists(yml_name):
        msg = 'No tournament.yml. Please use \'server\', \'host\' and \'group\' commands before use this command.\n'
        msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    tournament_setting = tl.loadYml(yml_name)
    msg = 'Current setting:\n' if len(body_txt) == 1 else 'Previous setting of {}:\n'.format(body_txt[1])
    for key, value in tournament_setting.items():
        msg += ' -{}: {}\n'.format(key, value)

    message.reply(msg)


@listen_to(r'^allow binary upload$')
@in_channel(ORGANIZER_CHANNEL_NAME)
def binary_upload_func(message):
    global bin_flag

    yml_name = '{}config/qualification_test.yml'.format(COMPETITION_MANAGER_PATH)
    if not os.path.exists(yml_name):
        msg = 'No qualification_test.yml. Please use \'server\', \'host\' and \'group\' commands before use this command.\n'
        msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    bin_flag = True
    print('bin_flag', bin_flag)
    msg = 'Team leaders can upload team binary now.'

    original_channel_id = message.body['channel']
    announce_channel_id = [tl.getChannelID(message, key['slack']) for key in ANNOUNCE_CHANNEL_NAME.values()]
    announce_channel_id.append(original_channel_id)
    tl.sendMessageToChannels(message=message,
                             message_str=msg,
                             channels=announce_channel_id,
                             default_id=original_channel_id)
    # if discordbot_flag:
    #     announce_channel_id = [key['discord'] for key in ANNOUNCE_CHANNEL_NAME.values()]
    #     for c in announce_channel_id:
    #         tl.sendMessageToDiscordChannel(msg, c)

    # confirmation
    target_server_ip = tl.loadYml(yml_name)['server']
    msg = 'Have you set-up the cpufreq governors to \'performance\' in {} ?\n'.format(target_server_ip)
    message.reply(msg)

@listen_to(r'^binary upload end$')
@in_channel(ORGANIZER_CHANNEL_NAME)
def binary_upload_func(message):
    global bin_flag
    bin_flag = False
    print('bin_flag', bin_flag)

    archived_time = datetime.datetime.now().strftime('%Y%m%d')
    msg = 'binary upload end.\n Current teams will be archived on {}{}/{}'.format(TEAMS_DIR, COMPETITION_NAME, archived_time)
    message.reply(msg)

    # save pre-uploaded binary
    archive_team_dir = '{}{}/{}/'.format(TEAMS_DIR, COMPETITION_NAME, archived_time)
    qualified_teams = tl.getQualifiedTeams()
    for q_team in qualified_teams:
        team_path = glob.glob(COMPETITION_MANAGER_PATH + 'qualified_team' + '/' + q_team + '.tar.*')
        os.makedirs(archive_team_dir, exist_ok=True)
        shutil.copy2(team_path[0], archive_team_dir)

    original_channel_id = message.body['channel']
    announce_channel_id = [tl.getChannelID(message, key['slack']) for key in ANNOUNCE_CHANNEL_NAME.values()]
    announce_channel_id.append(original_channel_id)
    msg = 'Team binaries cannot be uploaded now.'
    tl.sendMessageToChannels(message=message,
                             message_str=msg,
                             channels=announce_channel_id,
                             default_id=original_channel_id)
    # if discordbot_flag:
    #     announce_channel_id = [key['discord'] for key in ANNOUNCE_CHANNEL_NAME.values()]
    #     for c in announce_channel_id:
    #         tl.sendMessageToDiscordChannel(msg, c)


@listen_to(r'^test\w*')
@in_channel(ORGANIZER_CHANNEL_NAME)
def test_func(message):
    success = True
    txt_list = message.body['text'].split()
    if len(txt_list) != 2:
        msg = tl.getHelpMessageForOrganizers()
        message.send(msg)
        return

    if txt_list[1] == 'all' or txt_list == '*':
        test_teams = tl.getQualifiedTeams()
    else:
        test_teams = txt_list[1].split(',')
        qualified_teams = tl.getQualifiedTeams()
        for team in test_teams:
            if team not in qualified_teams:
                message.reply(team + ' is not in qualifications.')
                msg = tl.getHelpMessageForOrganizers()
                message.send(msg)
                return

    yml_name = '{}config/qualification_test.yml'.format(COMPETITION_MANAGER_PATH)
    if not os.path.exists(yml_name):
        msg = 'No qualification_test.yml. Please use \'server\', \'host\' and \'group\' commands before use this command.\n'
        msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    target_server_ip = tl.loadYml(yml_name)['server']

    global current_server_status
    if target_server_ip in current_server_status.keys():
        message.send('a game is conducted now at {}'.format(target_server_ip))
        return

    current_server_status[target_server_ip] = "test"

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
        # update qualification_test.yml
        conf['log_dir'] = log_dir
        conf['teams_dir'] = '/home/{}'.format(USERNAME)
        conf['teams'] = [t_team, 'agent2d']
        conf['server_conf'] = 'config/rcssserver/server_test.conf'
        tl.overwriteYml(yml_name, conf)

        qualified_dir = '{}qualified_team/'.format(COMPETITION_MANAGER_PATH)

        # sync tournament script
        tl.rsync(TOURNAMENT_PATH.rstrip('/'), '{}:/home/{}'.format(conf['server'], USERNAME))
        # sync config file of tournament
        tl.rsync(yml_name, '{}:/home/{}/tournament/config/{}'.format(conf['server'], USERNAME, yml_name.split('/')[-1]))
        # sync teams
        tl.rsync('{}{}'.format(qualified_dir, t_team), '{}:/home/{}'.format(conf['server'], USERNAME), delete=True)
        tl.rsync('{}/test/agent2d'.format(COMPETITION_MANAGER_PATH), '{}:/home/{}'.format(conf['server'], USERNAME), delete=True)

        # sync to host
        for h in conf['hosts']:
            if h == conf['server']:
                continue
            # sync tournament script
            tl.rsync(TOURNAMENT_PATH.rstrip('/'), '{}:/home/{}'.format(h, USERNAME))
            # sync config file of tournament
            tl.rsync(yml_name,
                     '{}:/home/{}/tournament/config/{}'.format(conf['server'], USERNAME, yml_name.split('/')[-1]))
            # sync teams
            tl.rsync('{}{}'.format(qualified_dir, t_team), '{}:/home/{}'.format(h, USERNAME), delete=True)
            tl.rsync('{}/test/agent2d'.format(COMPETITION_MANAGER_PATH), '{}:/home/{}'.format(h, USERNAME), delete=True)

        message.send(t_team + ' test start')
        _ = tl.startGame(conf['server'],
                         '/home/{}/tournament/config/{}'.format(USERNAME, yml_name.split('/')[-1]))
        message.send(t_team + ' test finish')

        # sync game logs to slackserver
        tl.rsync('{}:/home/{}/tournament/log'.format(conf['server'], USERNAME),
                 TOURNAMENT_PATH.rstrip('/'))
        # remove game logs in rcssserver
        tl.cmdAtRemoteServer(conf['server'],
                             'rm -r /home/{}/tournament/log'.format(USERNAME))

        # move logfiles to competition-manager
        os.makedirs(LOG_DIR + 'test/', exist_ok=True)
        shutil.move('{}{}'.format(TOURNAMENT_PATH, log_dir),
                    '{}test/{}/{}'.format(LOG_DIR, t_team, time))

    message.send('test complete')
    current_server_status.pop(target_server_ip)


@listen_to(r'^stop test$')
@in_channel(ORGANIZER_CHANNEL_NAME)
def stop_test_func(message):
    global stop_flag
    stop_flag = True
    msg = 'stop test'
    message.reply(msg)


@respond_to(r'^upload \w+')
def file_upload_func(message):
    message._client.reconnect()
    time.sleep(3)

    original_channel_id = message.body['channel']
    organizer_channel_id = tl.getChannelID(message, ORGANIZER_CHANNEL_NAME)

    user_id = message.body['user']

    try:
        email = message._client.users[user_id]['profile']['email']
    except KeyError as e:
        msg = 'Unknown email. The user entered after this system started.\nPlease restart this system'
        tl.sendMessageToChannels(message=message,
                                 message_str=msg,
                                 channels=[original_channel_id, organizer_channel_id],
                                 default_id=original_channel_id)
        print(e)
        return
    teamname = message.body['text'].split()[-1]

    yml_name = '{}config/qualification_test.yml'.format(COMPETITION_MANAGER_PATH)
    if not os.path.exists(yml_name):
        msg = 'No qualification_test.yml. Please use \'server\', \'host\' and \'group\' commands before use this command.\n'
        msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    global bin_flag
    if not bin_flag:
        msg = 'Binary upload is not allowed now.'
        message.reply(msg)
        return

    list_flag, only_mail_flag, only_team_flag, tmp_team = tl.checkRegistration(
        '{}config/maillist.txt'.format(COMPETITION_MANAGER_PATH),
        email, teamname)
    if not list_flag:
        if only_team_flag:
            msg = 'Only the team leader can upload team binary.'
        elif only_mail_flag:
            msg = 'Your team name may be \'{}\''.format(tmp_team, teamname)
        else:
            msg = 'Your team is not registered. Please ask organizers.'
        message.reply(msg)
        return

    global bin_test_queue
    if teamname in bin_test_queue:
        msg = 'Your team is already in binary-test que.'
        message.reply(msg)
        return
    bin_test_queue.append(teamname)

    target_server_ip = tl.loadYml(yml_name)['server']
    is_first_comment = False
    global current_server_status
    while True:
        if target_server_ip in current_server_status.keys():
            if not is_first_comment:
                msg = 'Another team is testing now.\n Please wait for a moment...'
                message.reply(msg)
                is_first_comment = True
            sleep(10)
        else:
            break

    current_server_status[target_server_ip] = 'test'
    if is_first_comment:
        msg = 'Sorry for late testing. Your binary test starts soon.'
        message.reply(msg)

    # qualified team directory that succeeded the binary test
    qualified_dir = COMPETITION_MANAGER_PATH + 'qualified_team/'
    os.makedirs(qualified_dir, exist_ok=True)

    # failed team directory that failed the binary test
    failed_dir = COMPETITION_MANAGER_PATH + 'failed_team/'
    os.makedirs(failed_dir, exist_ok=True)

    # temporary place in order to avoid illegal upload
    temporary_dir = COMPETITION_MANAGER_PATH + 'uploaded_team/'
    os.makedirs(temporary_dir, exist_ok=True)

    file_types = ['gzip', 'binary']
    download_file = dl.DownloadFile(file_types, temporary_dir)
    if 'files' in message.body.keys():
        filename = message.body['files'][0]['name']
        result = download_file.exe_download(message._body['files'][0])
    else:
        result = 'empty'

    print("bin download ", result)
    if result == 'ok':
        if '.tar.gz' not in filename and '.tar.xz' not in filename:
            msg = 'Please compress files using tar.gz (see thr binary upload manual for details)'
            tl.sendMessageToChannels(message=message,
                                     message_str=msg,
                                     channels=[original_channel_id, organizer_channel_id],
                                     default_id=original_channel_id)
            try:
                shutil.move('{}{}'.format(temporary_dir, filename), '{}{}'.format(failed_dir, filename))
            except (FileNotFoundError, FileExistsError) as e:
                print(e)
            bin_test_queue.remove(teamname)
            current_server_status.pop(target_server_ip)
            return
        if teamname != filename.split('.tar.')[0]:
            msg = 'Attached file\'s name [{}] is different from your command [{}]'.format(filename.split('.tar.gz')[0],
                                                                                          teamname)
            tl.sendMessageToChannels(message=message,
                                     message_str=msg,
                                     channels=[original_channel_id, organizer_channel_id],
                                     default_id=original_channel_id)
            try:
                shutil.move('{}{}'.format(temporary_dir, filename), '{}{}'.format(failed_dir, filename))
            except (FileNotFoundError, FileExistsError) as e:
                print(e)
            bin_test_queue.remove(teamname)
            current_server_status.pop(target_server_ip)
            return
        # !!! Assumption that uploaded files have more than 100 bytes
        file_size = os.path.getsize('{}{}'.format(temporary_dir, filename))
        if file_size < 100:
            msg = 'Attached file is empty or too small file size (<100bytes). Please try again.'
            tl.sendMessageToChannels(message=message,
                                     message_str=msg,
                                     channels=[original_channel_id, organizer_channel_id],
                                     default_id=original_channel_id)
            try:
                shutil.move('{}{}'.format(temporary_dir, filename), failed_dir + filename)
            except (FileNotFoundError, FileExistsError) as e:
                print(e)
            bin_test_queue.remove(teamname)
            current_server_status.pop(target_server_ip)
            return
    elif result == 'file type is not applicable.':
        message.reply('File type is not applicable.\n Applicable file type is tar.gz')
        try:
            shutil.move('{}{}'.format(temporary_dir, filename), '{}{}'.format(failed_dir, filename))
        except (FileNotFoundError, FileExistsError) as e:
            print(e)
        bin_test_queue.remove(teamname)
        current_server_status.pop(target_server_ip)
        return
    elif result == 'empty':
        message.reply('Attached file is not exist.')
        bin_test_queue.remove(teamname)
        current_server_status.pop(target_server_ip)
        return
    elif result == 'type null':
        message.reply(
            'Uploading binary may be too fast.\n please wait approx. 10 seconds after uploading binary is completed')
        try:
            shutil.move('{}{}'.format(temporary_dir, filename), '{}{}'.format(failed_dir, filename))
        except (FileNotFoundError, FileExistsError) as e:
            print(e)
        bin_test_queue.remove(teamname)
        current_server_status.pop(target_server_ip)
        return
    else:
        message.send('Uploading file is failed.')
        try:
            shutil.move('{}{}'.format(temporary_dir, filename), '{}{}'.format(failed_dir, filename))
        except (FileNotFoundError, FileExistsError) as e:
            print(e)
        bin_test_queue.remove(teamname)
        current_server_status.pop(target_server_ip)
        return

    msg = '{}:Binary upload succeeded.'.format(teamname)
    tl.sendMessageToChannels(message=message,
                             message_str=msg,
                             channels=[original_channel_id, organizer_channel_id],
                             default_id=original_channel_id)

    sleep(5)

    extract = subprocess.run(['{}/test/extend.sh'.format(COMPETITION_MANAGER_PATH),
                              filename,
                              temporary_dir,
                              COMPETITION_MANAGER_PATH], encoding='utf-8', stdout=subprocess.PIPE)
    if 'Error is not recoverable' in extract.stdout:
        message.reply("Uploaded file cannot be extracted. Please check the contents of the uploaded file.")
        bin_test_queue.remove(teamname)
        current_server_status.pop(target_server_ip)
        return

    if os.path.isdir('{}{}'.format(temporary_dir, teamname)):
        teamfiles = os.listdir('{}{}'.format(temporary_dir, teamname))
        if "start" not in teamfiles:
            message.reply("There is no \'start\' script in your file.")
            shutil.move('{}{}'.format(temporary_dir, filename), '{}{}'.format(failed_dir, filename))
            shutil.rmtree('{}{}'.format(temporary_dir, teamname))
            bin_test_queue.remove(teamname)
            current_server_status.pop(target_server_ip)
            return
        if "kill" not in teamfiles:
            message.send("There is no \'kill\' script in your file.")
            shutil.move('{}{}'.format(temporary_dir, filename), '{}{}'.format(failed_dir, filename))
            shutil.rmtree('{}{}'.format(temporary_dir, teamname))
            bin_test_queue.remove(teamname)
            current_server_status.pop(target_server_ip)
            return
        if "team.yml" not in teamfiles:
            ty_dict = {"country": teamname}
            tl.saveYml(ty_dict, '{}{}/team.yml'.format(temporary_dir, teamname))

        for curdir, dirs, files in os.walk(temporary_dir+teamname):
            try:
                os.chmod(curdir, 0o700)
                for file in files:
                    os.chmod(curdir+'/'+file, 0o700)
            except PermissionError as e:
                print('Permission Error ({}), but the upload procedure will continue...'.format(e.filename))

    else:
        message.reply(
            "The structure of team directory is wrong or the name of team directory is different from \'{}\'".format(
                teamname)
        )
        shutil.move('{}{}'.format(temporary_dir, filename), '{}{}'.format(failed_dir, filename))
        shutil.rmtree('{}'.format(temporary_dir))  # remove all files because bot cannot specified the problem-files.
        bin_test_queue.remove(teamname)
        current_server_status.pop(target_server_ip)
        return

    message.reply('Test game starts in about 2 minutes')

    upload_time = datetime.datetime.now().strftime('%Y%m%d%H%M')
    yml_name = '{}config/qualification_test.yml'.format(COMPETITION_MANAGER_PATH)
    log_dir = "log/" + teamname + "/" + upload_time

    tournament_conf = tl.loadYml(yml_name)

    # update qualification_test.yml
    tournament_conf['log_dir'] = log_dir
    tournament_conf['teams_dir'] = '/home/{}'.format(USERNAME)
    tournament_conf['teams'] = [teamname, 'agent2d']
    tournament_conf['server_conf'] = 'config/rcssserver/server_test.conf'
    tl.overwriteYml(yml_name, tournament_conf)

    # sync to server
    # sync tournament script
    tl.rsync(TOURNAMENT_PATH.rstrip('/'), '{}:/home/{}'.format(tournament_conf['server'], USERNAME))
    # sync config file of tournament
    tl.rsync(yml_name,
             '{}:/home/{}/tournament/config/{}'.format(tournament_conf['server'], USERNAME, yml_name.split('/')[-1]))
    # sync teams to server
    tl.rsync('{}{}'.format(temporary_dir, teamname), '{}:/home/{}'.format(tournament_conf['server'], USERNAME), delete=True)
    tl.rsync('{}test/agent2d'.format(COMPETITION_MANAGER_PATH),
             '{}:/home/{}'.format(tournament_conf['server'], USERNAME), delete=True)

    # sync to host
    for h in tournament_conf['hosts']:
        if h == tournament_conf['server']:
            continue
        # sync tournament script
        tl.rsync(TOURNAMENT_PATH.rstrip('/'), '{}:/home/{}'.format(h, USERNAME))
        # sync config file of tournament
        tl.rsync(yml_name, '{}:/home/{}/tournament/config/{}'.format(tournament_conf['server'], USERNAME,
                                                                     yml_name.split('/')[-1]))
        # sync teams to server
        tl.rsync('{}{}'.format(temporary_dir, teamname), '{}:/home/{}'.format(h, USERNAME), delete=True)
        tl.rsync('{}test/agent2d'.format(COMPETITION_MANAGER_PATH), '{}:/home/{}'.format(h, USERNAME), delete=True)

    result_game = tl.startGame(tournament_conf['server'],
                               '/home/{}/tournament/config/{}'.format(USERNAME, yml_name.split('/')[-1]))
    print(result_game.stdout)

    # sync game logs to slackserver
    tl.rsync('{}:/home/{}/tournament/log'.format(tournament_conf['server'], USERNAME),
             TOURNAMENT_PATH.rstrip('/'))
    # remove game logs in rcssserver
    tl.cmdAtRemoteServer(tournament_conf['server'],
                         'rm -r /home/{}/tournament/log'.format(USERNAME))

    # analyze the test
    result_analyze = subprocess.run(['{}/test/analyze_test.sh'.format(COMPETITION_MANAGER_PATH),
                                     TOURNAMENT_PATH + log_dir, LOGANALYZER_PATH],
                                    encoding='utf-8', stdout=subprocess.PIPE)
    print(result_analyze.stdout)

    if os.path.exists(TOURNAMENT_PATH + log_dir + '/match_1'):
        for f_name in os.listdir(TOURNAMENT_PATH + log_dir + '/match_1'):
            if ('rc' in f_name and '.gz' in f_name) or ('team_l' in f_name and '.log' in f_name):
                file_size = os.path.getsize(TOURNAMENT_PATH + log_dir + '/match_1/' + f_name)
                if file_size == 0:
                    message.reply('{} is empty'.format(f_name.rsplit('/', 1)[-1]))
                    continue
                tl.upload_file_s(TOURNAMENT_PATH + log_dir + '/match_1/' + f_name,
                                 message.body['channel'])

    # check disconnected players
    discon_index = result_analyze.stdout.find('DisconnectedPlayer')
    discon_p = result_analyze.stdout[discon_index + len('DisconnectedPlayer'):].replace('\n', '')
    print('discon_p', discon_p)

    # save the succeeded team_name to qualification.txt
    try:
        # success-process
        if discon_p != '' and int(discon_p) == 0 \
                and os.path.exists('{}/test/log_ana/{}.csv'.format(COMPETITION_MANAGER_PATH, teamname)):
            if os.path.exists('{}config/qualification.txt'.format(COMPETITION_MANAGER_PATH)):
                qualified_team = tl.getQualifiedTeams()
                if teamname not in qualified_team:
                    with open('{}config/qualification.txt'.format(COMPETITION_MANAGER_PATH), 'a') as q_txt_ad:
                        q_txt_ad.write(teamname + ',' + upload_time + '\n')
                else:
                    # already qualified. update the last uploaded time
                    with open('{}config/qualification.txt'.format(COMPETITION_MANAGER_PATH), 'r') as q_txt_r:
                        mod_q = []
                        lines = q_txt_r.readlines()
                        for line in lines:
                            if teamname == line.split(',')[0]:
                                tmp_line = teamname + ',' + upload_time + '\n'
                                mod_q.append(tmp_line)
                            else:
                                mod_q.append(line)
                    with open('{}config/qualification.txt'.format(COMPETITION_MANAGER_PATH), 'w') as q_txt_ad:
                        q_txt_ad.writelines(mod_q)
            else:
                with open('{}config/qualification.txt'.format(COMPETITION_MANAGER_PATH), 'w') as q_txt:
                    q_txt.write(teamname + ',' + upload_time + '\n')

            # success message
            msg = '{}:Binary test succeeded.'.format(teamname)
            tl.sendMessageToChannels(message=message,
                                     message_str=msg,
                                     channels=[original_channel_id, organizer_channel_id],
                                     default_id=original_channel_id)
            msg = 'Please check that your team worked correctly.'
            message.send(msg)

            # move the succeeded team in qualified_dir
            already_uploaded_files = glob.glob('{}{}*'.format(qualified_dir, teamname))
            for already_uploaded_file in already_uploaded_files:
                if os.path.isfile(already_uploaded_file):
                    os.remove(already_uploaded_file)
            shutil.move('{}{}'.format(temporary_dir, filename), '{}{}'.format(qualified_dir, filename))
            if os.path.exists('{}{}'.format(qualified_dir, teamname)):
                shutil.rmtree('{}{}'.format(qualified_dir, teamname))
            shutil.move('{}{}'.format(temporary_dir, teamname), '{}{}'.format(qualified_dir, teamname))

        # failed process
        else:
            # Illegal team_name
            if not os.path.exists('{}/test/log_ana/{}.csv'.format(COMPETITION_MANAGER_PATH, teamname)):
                msg = 'the team name is different from \'{}\''.format(teamname)
            # Disconnected Players
            elif discon_p != '' and int(discon_p) > 0:
                msg = '{} players were disconnected. Something may be wrong with the binary ' \
                      'while it could successfully connected to rcssserver at the beginning of the game.'.format(discon_p)
            # Unknown Error
            else:
                msg = '??? Something wrong ???'
            tl.sendMessageToChannels(message=message,
                                     message_str=msg,
                                     channels=[original_channel_id, organizer_channel_id],
                                     default_id=original_channel_id)
            shutil.move('{}{}'.format(temporary_dir, filename), '{}{}'.format(failed_dir, filename))
            shutil.rmtree('{}{}'.format(temporary_dir, teamname))

    except Exception:
        # print the error message
        import traceback
        traceback.print_exc()

        # failed message
        msg = '{}:Binary test failed.'.format(teamname)
        tl.sendMessageToChannels(message=message,
                                 message_str=msg,
                                 channels=[original_channel_id, organizer_channel_id],
                                 default_id=original_channel_id)
        shutil.move('{}{}'.format(temporary_dir, filename), '{}{}'.format(failed_dir, filename))
        shutil.rmtree('{}{}'.format(temporary_dir, teamname))

    # move logfiles to competition-manager
    try:
        os.makedirs(LOG_DIR + 'test/', exist_ok=True)
        shutil.move('{}{}'.format(TOURNAMENT_PATH, log_dir), '{}test/{}/{}'.format(LOG_DIR, teamname, upload_time))
    except FileNotFoundError as e:
        print(e)

    # reset game flag and bin-test-que
    bin_test_queue.remove(teamname)
    current_server_status.pop(target_server_ip)


@listen_to(r'^clear$')
@in_channel(ORGANIZER_CHANNEL_NAME)
def clear_qualification_and_maillist(message):
    qualification_path = '{}config/qualification.txt'.format(COMPETITION_MANAGER_PATH)
    if os.path.exists(qualification_path):
        with open(qualification_path, 'w') as _:
            pass

    maillist_path = '{}config/maillist.txt'.format(COMPETITION_MANAGER_PATH)
    if os.path.exists(maillist_path):
        with open(maillist_path, 'w') as m_txt:
            m_txt.write('hogehoge@gmail.com,teamname1\nfugafuga@gmail.com,teamname2\n')

    message.reply('setting files are cleared.')


@listen_to(r'^register \S+$')
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
        m_txt.write(','.join(splitted_body_txt) + '\n')
    message.reply('{},{} are registered in maillist.txt'.format(splitted_body_txt[0], splitted_body_txt[1]))


@listen_to(r'^share \w+$')
@in_channel(ORGANIZER_CHANNEL_NAME)
def share_file_func(message):
    if not google_drive_flag:
        msg = 'google_drive flag is False. Please use after google_drive_flag True by using \'gdrive\' command.'
        message.reply(msg)
        return

    txt = message.body['text'].split()
    if len(txt) != 2 or (txt[-1] != 'logs' and txt[-1] != 'teams'):
        msg = tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    gdrive = tl.MyGoogleDrive()
    upload_target = LOG_DIR + COMPETITION_NAME if txt[-1] == 'logs' else TEAMS_DIR + COMPETITION_NAME
    gdrive.upload(upload_target, prefix=txt[-1])

    msg = 'Game logs' if txt[-1] == 'logs' else 'Team binaries'
    msg = '{} are available at https://drive.google.com/drive/folders/{}'.format(msg, GOOGLE_DRIVE_FOLDER_ID)

    original_channel_id = message.body['channel']
    announce_channel_id = [tl.getChannelID(message, key['slack']) for key in ANNOUNCE_CHANNEL_NAME.values()]
    announce_channel_id.append(original_channel_id)

    tl.sendMessageToChannels(message=message,
                             message_str=msg,
                             channels=announce_channel_id,
                             default_id=original_channel_id)
    if discordbot_flag:
        announce_channel_id = [key['discord'] for key in ANNOUNCE_CHANNEL_NAME.values()]
        for c in announce_channel_id:
            tl.sendMessageToDiscordChannel(msg, c)


@listen_to(r'^recovery mode \w+$')
@in_channel(ORGANIZER_CHANNEL_NAME)
def switch_recovery_mode(message):
    txt_list = message.body['text'].split()
    if len(txt_list) != 3:
        msg = 'Illegal input\n'
        msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    if txt_list[-1] != 'true' and txt_list[-1] != 'false':
        msg = 'You can choose \'true\' or \'false\' in this command\n'
        msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    global recovery_mode
    recovery_mode = True if txt_list[-1] == 'true' else False
    msg = 'recovery_mode is changed to \'{}\'\n'.format(txt_list[-1])
    msg += '!!!!! you can reset bin_test_queue and gameflag. Please switch back to false after your recovery !!!!!'
    message.reply(msg)
    return


@listen_to(r'^reset gameflag .+$')
@in_channel(ORGANIZER_CHANNEL_NAME)
def reset_gameflag(message):
    txt_list = message.body['text'].split()
    if len(txt_list) != 3:
        msg = 'Illegal input\n'
        msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    global recovery_mode
    if not recovery_mode:
        msg = 'This command can only available in recovery mode.\n'
        msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    target_server_ip = txt_list[-1]
    global current_server_status
    if not target_server_ip in current_server_status.keys():
        msg = '{} is alreagy free.'.format(target_server_ip)
        message.reply(msg)
        return

    current_server_status.pop(target_server_ip)
    message.reply('reset {}'.format(target_server_ip))


@listen_to(r'^reset test queue .+$')
@in_channel(ORGANIZER_CHANNEL_NAME)
def reset_test_queue(message):
    txt_list = message.body['text'].split()
    if len(txt_list) != 4:
        msg = 'Illegal input\n'
        msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    global recovery_mode
    if not recovery_mode:
        msg = 'This command can only available in recovery mode.\n'
        msg += tl.getHelpMessageForOrganizers()
        message.reply(msg)
        return

    global bin_test_queue
    if txt_list[-1] in bin_test_queue:
        bin_test_queue.remove(txt_list[-1])
        msg = '{} is removed from queue'.format(txt_list[-1])
    else:
        msg = '{} is not exist in queue'.format(txt_list[-1])
    message.reply(msg)

