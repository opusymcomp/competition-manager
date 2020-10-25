# coding: utf-8
import plugins.tools as tl
import datetime
import subprocess
import plugins.bin_download as dl
import os
import yaml
import shutil

from slackbot.bot import respond_to
from slackbot.bot import listen_to
from .utils import in_channel

from time import sleep


with open( "./conf.yml" ) as fy_r:
    conf = yaml.safe_load( fy_r )
home = os.path.expanduser("~") + "/"
loganalyzer_path = home + conf['loganalyzer_path']
tournament_path = home + conf['tournament_path']
competition_conf_path = conf['competition_conf_path']
organize_ch_n = conf["organize_ch_n"]
announce_ch_n = conf['announce_ch_n']
config = conf['conf_path']
config_yml = tournament_path + config
test_config_yml = tournament_path + conf['test_conf_path']
db_access_token = conf['dbx_token']
db_boot_dir = conf['dbx_boot_dir']
competition_name = conf['competition_name']

bin_flag = False
dbx_flag = False
test_flag = False
announce_flag = False
game_flag = False

if dbx_flag:
    db = tl.MyDropbox(db_access_token, db_boot_dir)
    db.createFolder()

if os.environ.get("PATH"):
    os.environ["PATH"] = loganalyzer_path + ":" + os.environ["PATH"]
else:
    os.environ["PATH"] = loganalyzer_path


@listen_to(r'^help$')
@in_channel(organize_ch_n)
def listen_func(message):
    msg = '[Command list]\n -team : Show binary test completion team.\n -group* TEAMNAME... : Create a group and ' \
          'select teams to run the round-robin. (ex. groupA teamA,temaB,teamC,...)\n -start group* : Start ' \
          'round-robon. (ex. start groupA) '
    message.reply(msg)


@listen_to(r'^team$')
@in_channel(organize_ch_n)
def listen_func(message):
    msg = 'Create a group and select teams to run the round-robin. (ex. groupA teamA,teamB,teamC,...)\n'
    opplist = tl.getOpponent()
    for i in range(len(opplist)):
        msg = msg + str(i + 1) + ' : ' + opplist[i] + '\n'
    message.reply(msg)


@listen_to(r'^group\w*')
@in_channel(organize_ch_n)
def listen_func(message):
    setting = message.body['text'].split()
    ans_flag = 'help'
    if len( setting ) == 1:
        if setting[0] == 'group':
            ans_flag = 'help'
        else:
            ans_flag = 'status'
    elif len( setting ) == 2:
        ans_flag = 'help'
    elif len( setting ) == 3:
        ans_flag = 'set'

    if ans_flag == 'help':
        msg = 'group* [key] [values] : setting [key] [values] in group*\n group* : showing group* setting'
        message.reply(msg)
    elif ans_flag == 'status':
        if len( setting ) == 1:
            group_keys = tl.listYml( competition_conf_path, setting[0] )
            for g_key in group_keys:
                key_values = tl.listGroupYml( competition_conf_path, setting[0], g_key )
                if type(key_values) != list:
                    key_values = key_values + '\n'
                else:
                    key_values = '\n-'.join( key_values )
                msg = '\n' + g_key + '\n-' + key_values
                message.send( msg )
        else:
            msg = tl.listGroupYml( competition_conf_path, setting[0], setting[1] )
        if msg == False:
            message.reply('error : show commandline')
    elif ans_flag == 'set':
        setting[2] = setting[2].split(',')
        flag = False
        if setting[1] in tl.getTourYmlKeys( config_yml ):
            flag = True
        if flag:
            tl.storeGroupYml( competition_conf_path, setting[0], setting[1], setting[2] )
            message.reply('setting config completed')
        else:
            message.reply(setting[1] + ' is not in config keys')

    # text_flag = True
    # if len( setting ) != 2:
    #     text_flag = False
    # elif setting[0] in "group":
    #     text_flag = False

    # if text_flag == True:
    #     group = setting[0] #''.join(setting[:6])
    #     print('setting:', setting)
    #     print('group:', group)
    #     gtxt = tl.saveGroup(setting)
    #     groups = setting[1].split(',')

    #     tl.writeYml( competition_conf_path, group, groups )

    #     msg = 'Created round-robin ' + group + '.\n'
    #     roundrobin = groups #tl.getRoundrobin(setting, gtxt)
    #     print('roundrobin:', roundrobin)
    #     msg = msg + 'You choose ' + str(
    #         roundrobin) + ' for the target teams.\n Confirmation. \n -Group : [' + group + '] \n -Target teams : ' + str(
    #             roundrobin) + '\n'
    #     message.reply(msg)
    #     msg = 'Enter "start group*" to run the round-robin'
    #     message.reply(msg)


@listen_to(r'^start \w+')
@in_channel(organize_ch_n)
def cool_func(message):
    global game_flag
    if not game_flag or game_flag:
        dt_start = datetime.datetime.now().strftime('%Y%m%d%H%M')

        # startgroup = message.body['text']
        # group = ''.join(startgroup[6:])
        txt_flag = ''
        txt_list = message.body['text'].split()
        group = txt_list[1]
        if len( txt_list ) == 2 and 'group' in group:
            if os.path.exists( competition_conf_path ):
                with open(competition_conf_path) as fy_c:
                    groups_yml = yaml.safe_load(fy_c)
                if group in groups_yml.keys():
                    group_yml = groups_yml[ group ]
                else:
                    txt_flag = 'not in g_conf'
            else:
                txt_flag = 'not exist'
        else:
            txt_flag = 'help'

        if txt_flag == 'help':
            message.send('start group* : Start round-robon. (ex. start groupA)')
        elif txt_flag == 'not exist':
            message.send('competition conf does not exist')
        elif txt_flag == 'not in g_conf':
            message.send('group conf is not in competition conf')
        elif txt_flag == '':
            #roundrobin = tl.getStartgroup(startgroup)
            msg = 'The ' + group + ' starts soon \n Start time : ' + dt_start + '\n I will notify you when the game ' \
                  'finished.\n '
            message.reply(msg)
            message.react('+1')
            ori_channel = message.body['channel']
            message.body['channel'] = tl.getChannelID(message, announce_ch_n)
            message.send(msg)
            message.body['channel'] = ori_channel

            game_flag = True
            with open(config_yml) as fy_r:
                conf = yaml.safe_load(fy_r)

            for conf_key in group_yml.keys():
                conf[conf_key] = group_yml[conf_key]

        # if conf['mode'] == 'single_match' and game_flag:
        #     for num_l in range(len(roundrobin) - 1):
        #         for num_r in range(num_l + 1, len(roundrobin)):
        #             dt_now_M = datetime.datetime.now().strftime('%Y%m%d%H%M')

        #             matchteam = []
        #             matchteam.append(roundrobin[num_l])
        #             matchteam.append(roundrobin[num_r])

        #             # with open( config_yml ) as fy_r:
        #             #     conf = yaml.safe_load( fy_r )
        #             conf['teams'] = matchteam
        #             log_d = conf['log_dir'].split('/')

        #             # log/a/などの様に前後に空の要素が出来るときの処理
        #             for i in range(log_d.count("")):
        #                 log_d.remove("")

        #             conf['log_dir'] = ""
        #             find_g = [s for s in log_d if "group" in s]
        #             if len(find_g) > 0:
        #                 for n in range(len(log_d)):
        #                     if "group" in log_d[n]:
        #                         break
        #                     conf['log_dir'] = conf['log_dir'] + log_d[n] + '/'
        #             else:
        #                 for n in range(len(log_d)):
        #                     conf['log_dir'] = conf['log_dir'] + log_d[n] + '/'
        #             conf['log_dir'] = conf['log_dir'] + group + '/' + dt_now_M

        #             with open(config_yml, 'w') as fy_w:
        #                 yaml.dump(conf, fy_w, default_flow_style=False)
        #             msg = 'match start' + str(matchteam)
        #             message.send(msg)

        #             subprocess.run([tournament_path + 'start.sh', '--config=' + config])

        #             # arg=[]
        #             # arg.append(tournament_path)
        #             # arg.append(conf['log_dir'])
        #             # arg.extend(roundrobin)
        #             # arg = " ".join(arg)
        #             # result = subprocess.run( ['../gametools/results/result.sh', str(arg)] )

        #             rank = subprocess.run(['../gametools/results/rank.sh', str(group)], encoding='utf-8',
        #                                   stdout=subprocess.PIPE)
        #             print(rank.stdout)
        #             # standing.main(group)

        #             msg = 'match finish' + str(matchteam)
        #             message.send(msg)

        if conf['mode'] == 'group' and game_flag:
            dt_now_M = datetime.datetime.now().strftime('%Y%m%d%H%M')
            #conf['teams'] = roundrobin

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

            conf['teams_dir'] = home
            with open(config_yml, 'w') as fy_w:
                yaml.dump(conf, fy_w, default_flow_style=False)

            group_match_sim = subprocess.run([tournament_path + 'start.sh', '--config=' + config + ' --simulate'],
                                             encoding='utf-8', stdout=subprocess.PIPE)
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
            with open('./match_list.yml', 'w') as fw:
                yaml.dump(match_dict, fw, default_flow_style=False)

            group_match = subprocess.run(
                [tournament_path + 'start.sh', '--config='+config],
                encoding='utf-8',
                stdout=subprocess.PIPE )
        if announce_flag:
            match_n = 0
            with open('./match_list.yml') as fr:
                match_list = yaml.safe_load(fr)

            for n in os.listdir(tournament_path + conf['log_dir']):
                if 'match' in n:
                    num = n[len('match_'):]
                    if match_n < int(num):
                        match_n = int(num)
            with open( tournament_path + conf['log_dir'] + '/results.log', 'r') as r_log:
                log_lines = r_log.readlines()
            header = log_lines[0].split(',')
            elm = log_lines[-1].split(',')
            result_line_dict = { header[i].strip():elm[i].strip() for i in range( len(header) ) }

            if dbx_flag:
                match_dir = tournament_path + conf['log_dir'] + '/match_' + str(match_n)
                db_match_dir = db_boot_dir + '/match_' + str(match_n)
                db = tl.MyDropbox(db_access_token, db_match_dir)
                db.createFolder()
                for match_file in os.listdir(match_dir):
                    with open( match_dir + '/' + match_file, 'rb') as m_f:
                        f_body = m_f.read()
                        db.uploadFiles(f_body, match_file)
                db_link = db.get_shared_link( db_match_dir )
            msg = 'match end\n' \
                  + match_list['match_' + str(match_n)]['team_l'] + '_' \
                  + result_line_dict['left score'] + ' vs ' \
                  + result_line_dict['right score'] + '_' \
                  + match_list['match_' + str(match_n)]['team_r']
            if dbx_flag:
                msg += '\n' + db_link
            message.send(msg)
            ori_channel = message.body['channel']
            message.body['channel'] = tl.getChannelID(message, announce_ch_n)
            message.send(msg)
            message.body['channel'] = ori_channel

        dt_finish = datetime.datetime.now().strftime('%Y%m%d%H%M')
        msg = 'The ' + group + ' finish! \n Finish time : ' + dt_finish
        message.send(msg)
        message.body['channel'] = tl.getChannelID(message, announce_ch_n)
        message.send(msg)
        message.body['channel'] = ori_channel
        game_flag = False
    else:
        message.send("do not start a game while other game")


@listen_to(r'^announce match$')
@in_channel(organize_ch_n)
def listen_func(message):
    with open(config_yml) as fy_r:
        conf = yaml.safe_load(fy_r)
    match_n = 0
    global announce_flag
    progress_flag = False
    while game_flag and not test_flag:
        announce_flag = True
        with open('./match_list.yml') as fr:
            match_list = yaml.safe_load(fr)

        for n in os.listdir(tournament_path + conf['log_dir']):
            if 'match' in n:
                num = n[len('match_'):]
                if match_n < int(num):
                    match_n = int(num)
                    progress_flag = True
        if progress_flag:
            pre_match = match_n - 1

            if pre_match >= 1:
                with open( tournament_path + conf['log_dir'] + '/results.log', 'r') as r_log:
                    log_lines = r_log.readlines()
                header = log_lines[0].split(',')
                elm = log_lines[-1].split(',')
                result_line_dict = { header[i].strip():elm[i].strip() for i in range( len(header) ) }

                if dbx_flag:
                    match_dir = tournament_path + conf['log_dir'] + '/match_' + str(pre_match)
                    db_match_dir = db_boot_dir + '/match_' + str(pre_match)
                    db = tl.MyDropbox(db_access_token, db_match_dir)
                    db.createFolder()
                    for match_file in os.listdir(match_dir):
                        with open( match_dir + '/' + match_file, 'rb') as m_f:
                            f_body = m_f.read()
                        db.uploadFiles(f_body, match_file)
                    db_link = db.get_shared_link( db_match_dir )

                msg = 'match end\n' \
                      + match_list['match_' + str(pre_match)]['team_l'] + '_' \
                      + result_line_dict['left score'] + ' vs ' \
                      + result_line_dict['right score'] + '_' \
                      + match_list['match_' + str(pre_match)]['team_r']
                if dbx_flag:
                    msg += '\n' + db_link
                message.send(msg)
                ori_channel = message.body['channel']
                message.body['channel'] = tl.getChannelID(message, announce_ch_n)
                message.send(msg)
                message.body['channel'] = ori_channel

            msg = 'match start\n' \
                  + match_list['match_' + str(match_n)]['team_l'] + ' vs ' \
                  + match_list['match_' + str(match_n)]['team_r']
            message.send(msg)
            ori_channel = message.body['channel']
            message.body['channel'] = tl.getChannelID(message, announce_ch_n)
            message.send(msg)
            message.body['channel'] = ori_channel

            progress_flag = False
        sleep(5)
    announce_flag = False
    # if match_n == match_list['max_match']:
    #     if os.path.exists( tournament_path + conf['log_dir'] +'/match_'+ str(match_n) +'/match.yml' ):
    #         message.send(
    #             'match end '
    #             + match_list[ 'match_' + str(match_n) ]['team_l']
    #             + 'vs'
    #             + match_list[ 'match_' + str(match_n) ]['team_r']
    #        )

@listen_to(r'^check_matches \w+')
@in_channel(organize_ch_n)
def listen_func(message):

    startgroup = message.body['text']
    group = startgroup.split()[1]
    roundrobin = tl.getTeamsInGroup(group)

    with open(config_yml) as fy_r:
        conf = yaml.safe_load(fy_r)

    conf['teams'] = roundrobin

    with open(config_yml, 'w') as fy_w:
        yaml.dump(conf, fy_w, default_flow_style=False)

    group_match_sim = subprocess.run([tournament_path + 'start.sh', '--config=' + config + ' --simulate'],
                                     encoding='utf-8', stdout=subprocess.PIPE)
    matches = group_match_sim.stdout.split("\n")
    msg = ''
    for i in range(len(matches)-2):
        if i == 0:
            continue
        elif i > 1:
            mod_row = matches[i].split()
            mod_row[1] = mod_row[1].strip(conf['teams_dir'])
            mod_row[3] = mod_row[3].strip(conf['teams_dir'])
            matches[i] = " ".join(mod_row)
        msg += matches[i] + '\n'
    message.send( msg )

# @listen_to(r'^syn_teams \w+')
# @in_channel(organize_ch_n)
# def listen_func(message):

#     startgroup = message.body['text']
#     groups = startgroup.split()[1].split(',')
#     for group in groups:
#         teams = tl.getTeamsInGroup( group )


@listen_to(r'^add_comp \w+')
@in_channel(organize_ch_n)
def listen_func(message):
    text_comp = message.body['text']
    computers = text_comp.split()[1].split(',')
    tl.addYml( competition_conf_path, 'computers', computers )

@listen_to(r'^delete_comp \w+')
@in_channel(organize_ch_n)
def listen_func(message):
    text_comp = message.body['text']
    computers = text_comp.split()[1].split(',')
    tl.deleteYml( competition_conf_path, 'computers', computers )

@listen_to(r'^computers$')
@in_channel(organize_ch_n)
def listen_func(message):
    comp_list = tl.listYml( competition_conf_path, 'computers' )
    msg = '\n'.join( comp_list )
    message.send( msg )

@listen_to(r'^add_server \w+')
@in_channel(organize_ch_n)
def listen_func(message):
    text_comp = message.body['text']
    computers = text_comp.split()[1].split(',')
    tl.addYml( competition_conf_path, 'server', computers )

# @listen_to(r'^create_ \w+')
# @in_channel(organize_ch_n)
# def listen_func(message):
#     text_comp = message.body['text']
#     computers = text_comp.split()[1].split(',')
#     tl.addYml( competition_conf_path, 'server', computers )

# @listen_to(r'^country \w+')
# @in_channel(organize_ch_n)
# def listen_func(message):
#     print("test")
#     texts = message.body['text'].split()
#     print(texts)
#     if len(texts) == 3:
#         cmd, team, country = texts
#         teams = tl.getOpponent()
#         if team in teams:
#             with open( home+team+"/team.yml" ) as ty_w:
#             ty_dict={ "country": teamname }
#             with open( teamdir+"/team.yml", 'w' ) as ty_w:
#                 yaml.dump( ty_dict, ty_w, default_flow_style=False )
#                 conf = yaml.safe_load( fy_r )

#     else:
#         message.send("miss args:"+texts)


@respond_to(r'^upload start$')
def listen_func(message):
    print(message.body['user'])
    org_mem = tl.getChannelMembers(message, organize_ch_n)
    if message.body['user'] in org_mem:  # organizer's id
        global bin_flag
        bin_flag = True
        print('bin_flag', bin_flag)
        msg = 'binary upload start'
        message.reply(msg)
    else:
        msg = 'Not allowed'
        message.reply(msg)


@respond_to(r'^upload end$')
def listen_func(message):
    org_mem = tl.getChannelMembers(message, organize_ch_n)
    if message.body['user'] in org_mem:  # organizer's id
        global bin_flag
        bin_flag = False
        print('bin_flag', bin_flag)
        msg = 'binary upload end'
        message.reply(msg)
    else:
        msg = 'Not allowed'
        message.reply(msg)


@respond_to(r'^gameflag false$')
def listen_func(message):
    org_mem = tl.getChannelMembers(message, organize_ch_n)
    if message.body['user'] in org_mem:  # organizer's id
        global game_flag
        game_flag = False
        msg = 'enable to start a game'
        message.reply(msg)
    else:
        msg = 'Not allowed'
        message.reply(msg)


@respond_to(r'^testflag false$')
def listen_func(message):
    org_mem = tl.getChannelMembers(message, organize_ch_n)
    if message.body['user'] in org_mem:  # organizer's id
        global test_flag
        test_flag = False
        msg = 'enable to start a test'
        message.reply(msg)
    else:
        msg = 'Not allowed'
        message.reply(msg)


# @respond_to(r'^adding$')
# def listen_func(message):
#     if message.body['user'] == organizer_id: #organizer's id
#         userid = message.body['user']
#         email = message.channel._client.users[userid]['profile']['email']
#         mail_path='../../test/maillist.txt'
#         if os.path.exists(mail_path):
#             with open( mail_path, 'r' ) as q_txt:
#                 q_teams = q_txt.read()
#             if email not in q_teams:
#                 with open( mail_path, 'a+' ) as q_txt_ad:
#                     q_txt_ad.writelines(email+'\n')
#             else:
#                 with open( mail_path, 'a+' ) as q_txt_ad:
#                     q_txt_ad.writelines(email+'\n')
#             message.reply("add mail")

# @respond_to('^test$')
# def listen_func(message):
#     message.send('test')
#     db = tl.MyDropbox(db_access_token, db_boot_dir)
#     db.createFolder()
#     db.viewFiles()



@respond_to('^bin \w+')
def file_download(message):
    userid = message.body['user']
    email = message.channel._client.users[userid]['profile']['email']
    with open('../../test/maillist.txt', mode='rt', encoding='utf-8') as f:
        for line in f:
            l_mail = line.strip()
            print(l_mail)
            if l_mail == email:
                list_flag = True
                break
            else:
                list_flag = False
    global game_flag
    global test_flag
    err_flag = False
    if bin_flag == True and list_flag == True and not game_flag and not test_flag:
        test_flag = True
        teamname = message.body['text']
        teamname = ''.join(teamname[4:])
        print("test teamname:", teamname)
        teamdir = home + teamname
        file_types = ['gzip', 'binary']
        download_file = dl.DownloadFile(file_types, home)
        if 'files' in message._body.keys():
            filename = message._body['files'][0]['name']
            result = download_file.exe_download(message._body['files'][0])
        else:
            result = 'empty'
        print("bin download ", result)
        if result == 'ok':
            msg = 'binary upload complete'
            ori_channel = message.body['channel']
            message.body['channel'] = tl.getChannelID(message, organize_ch_n)
            message.send(teamname + msg)
            message.body['channel'] = ori_channel
            message.send(msg)
        elif result == 'file type is not applicable.':
            message.send('file type is not applicable.\n applicable file type is tar.gz')
            err_flag = True
        elif result == 'empty':
            message.send('attached file is not exist.')
            err_flag = True
        elif result == 'type null':
            message.send('uploading binary may be too fast.\n please wait approx. 10 seconds after uploading binary is completed')
            err_flag = True
        else:
            message.send('uploading file is failed.')
            err_flag = True

        sleep(5)

        if os.path.isdir(teamdir):
            preT_path = home + 'preteams/'
            os.makedirs( preT_path, exist_ok = True )
            if os.path.isdir( preT_path + teamname ):
                shutil.rmtree( preT_path + teamname )
            shutil.move( teamdir, preT_path )

        if not err_flag:
            extract = subprocess.run(['../../test/extend.sh', filename], encoding='utf-8', stdout=subprocess.PIPE)
            with open('../../test/stdlog.txt', 'r') as std:
                extractlog = std.read()
            if 'Error is not recoverable' in extractlog:
                message.send("uploaded file cannot be extracted")
                err_flag = True

        if os.path.isdir(teamdir):
            teamfiles = os.listdir(teamdir)
            if "start" not in teamfiles:
                message.send("no start")
                err_flag = True
            if "kill" not in teamfiles:
                message.send("no kill")
                err_flag = True
            if "team.yml" not in teamfiles:
                ty_dict = {"country": teamname}
                with open(teamdir + "/team.yml", 'w') as ty_w:
                    yaml.dump(ty_dict, ty_w, default_flow_style=False)
            for excecuted in teamfiles:
                os.chmod(teamdir + "/" + excecuted, 0o777)
        elif not err_flag:
            err_flag = True
            message.send(
                "team directory is not directory or team directory name is different"
            )

        if not err_flag and not game_flag:
            message.send('binary test start (please wait approx. 2 min.)')
            game_flag = True
            time = datetime.datetime.now().strftime('%Y%m%d%H%M')
            with open(test_config_yml) as fy_r:
                conf = yaml.safe_load(fy_r)

            conf['log_dir'] = "log/" + teamname + "/" + time
            conf['teams_dir'] = home
            conf['teams'] = [ teamname, 'agent2d' ]

            with open(test_config_yml, 'w') as fy_w:
                yaml.dump(conf, fy_w, default_flow_style=False)

            test_start = subprocess.run([tournament_path + 'start.sh', '--config=' + test_config_yml],
                                        encoding='utf-8', stdout=subprocess.PIPE)
            print(test_start.stdout)
            analyze_test = subprocess.run(['../../test/analyze_test.sh',
                                           tournament_path + conf['log_dir'], loganalyzer_path],
                                          encoding='utf-8', stdout=subprocess.PIPE)
            print(analyze_test.stdout)

            if os.path.exists( tournament_path + conf['log_dir'] + '/match_1' ):
                for f_name in os.listdir( tournament_path + conf['log_dir'] + '/match_1' ):
                    if 'rc' in f_name and '.gz' in f_name:
                        tl.upload_file_s( tournament_path + conf['log_dir'] + '/match_1/' + f_name, message.body['channel'] )

            discon_index = analyze_test.stdout.find('DisconnectedPlayer')
            nl_index = analyze_test.stdout[discon_index:].find('\n')
            discon_p = analyze_test.stdout[discon_index + len('DisconnectedPlayer'):discon_index + nl_index]
            print('discon_p', discon_p)
            if discon_p == '':
                message.send('test failed')
            elif int(discon_p) == 0:
                q_path = '../../test/qualification.txt'
                if os.path.exists(q_path):
                    with open(q_path, 'r') as q_txt:
                        q_teams = q_txt.readlines()
                    q_teams_row = "".join(q_teams)
                    if teamname not in q_teams_row:
                        with open(q_path, 'a+') as q_txt_ad:
                            q_txt_ad.writelines(teamname + ',' + time + '\n')
                    else:
                        mod_q = []
                        for line in q_teams:
                            if teamname in line:
                                line = teamname + ',' + time + '\n'
                                mod_q.append(line)
                            else:
                                mod_q.append(line)
                        with open(q_path, 'w') as q_txt_ad:
                            q_txt_ad.writelines(mod_q)
                else:
                    with open(q_path, 'w') as q_txt:
                        q_txt.writelines(teamname + ',' + time + '\n')
                msg = 'binary test complete'
                ori_channel = message.body['channel']
                message.body['channel'] = tl.getChannelID(message, organize_ch_n)
                message.send(teamname + msg)
                message.body['channel'] = ori_channel
                message.send(msg)
            elif int(discon_p) > 0:
                message.send('disconnected player(s) ' + discon_p)
            else:
                message.send('test failed')
                ori_channel = message.body['channel']
                message.body['channel'] = tl.getChannelID(message, organize_ch_n)
                message.send(teamname + ' test failed')
                message.body['channel'] = ori_channel
            game_flag = False
            test_flag = False
        elif game_flag:
            message.reply("Another team is testing.\n Just a moment, please.")
            test_flag = False
        elif err_flag:
            test_flag = False
    elif game_flag:
        message.reply("do not start a game while other game")
    else:
        msg = 'Not allowed'
        message.reply(msg)


@respond_to('^clear qualification$')
def file_download(message):
    org_mem = tl.getChannelMembers(message, organize_ch_n)
    if message.body['user'] in org_mem:  # organizer's id
        q_path = '../../test/qualification.txt'
        if os.path.exists(q_path):
            with open(q_path, 'w') as q_txt:
                pass
