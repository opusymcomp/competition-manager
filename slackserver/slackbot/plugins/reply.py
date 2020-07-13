# coding: utf-8
import plugins.tools as tl
import datetime
import subprocess
import requests
import codecs
import slackbot_settings
import plugins.bin_download as dl
import os
import yaml
from time import sleep


from slackbot.bot import respond_to
from slackbot.bot import listen_to
from slackbot.bot import default_reply
from .utils import in_channel

from time import sleep

home=os.path.expanduser("~")+"/"
loganalyzer_path=home+'competition-manager/loganalyzer3/'
tournament_path=home+'competition-manager/tournament/'
config='config/sample/sample.yml'
config_yml = tournament_path+config
organize_ch_n="organizer"
bin_flag=False
organizer_id="ORGANIZER_ID"
game_flag=False

if os.environ.get("PATH"):
    os.environ["PATH"]=loganalyzer_path+":"+os.environ["PATH"]
else:
    os.environ["PATH"]=loganalyzer_path

@listen_to(r'^help$')
@in_channel(organize_ch_n)
def listen_func(message):
    msg = '[Command list]\n -team : Show binary test completion team.\n -group* TEAMNAME... : Create a group and select teams to run the round-robin. (ex. groupA teamA,temaB,teamC,...)\n -start group* : Start round-robon. (ex. start groupA)'
    message.reply(msg)

@listen_to(r'^team$')
@in_channel(organize_ch_n)
def listen_func(message):
    msg = 'Create a group and select teams to run the round-robin. (ex. groupA teamA,teamB,teamC,...)\n'
    opplist = tl.getOpponent()
    for i in range(len(opplist)):
        msg = msg  + str(i+1) +  ' : ' + opplist[i]+ '\n'
    message.reply(msg)

@listen_to(r'^group\w+')
@in_channel(organize_ch_n)
def listen_func(message):
    setting = message.body['text']
    group =  ''.join(setting[:6])
    print('setting:',setting)
    print('group:',group)
    gtxt = tl.saveGroup(setting)
    msg = 'Created round-robin ' + group + '.\n'
    roundrobin = tl.getRoundrobin(setting, gtxt)
    print('roundrobin:',roundrobin)
    msg = msg + 'You choose ['+ str(roundrobin) + '] for the target teams.\n Confirmation. \n -Group : ['+ group +'] \n -Target teams : [' + str(roundrobin) + ']\n'
    message.reply(msg)
    msg = 'Enter "start group*" to run the round-robin'
    message.reply(msg)

@listen_to(r'^start \w+')
@in_channel(organize_ch_n)
def cool_func(message):
    global game_flag
    if not game_flag:
        game_flag=True
        dt_start = datetime.datetime.now().strftime('%Y%m%d%H%M')
        startgroup = message.body['text']
        group =  ''.join(startgroup[6:])
        roundrobin = tl.getStartgroup(startgroup)
        msg = 'The ' + group +' starts soon \n Start time : ' + dt_start + '\n I will notify you when the game finished.\n'
        message.reply(msg)
        message.react('+1')
        ori_channel=message.body['channel']
        message.body['channel']='C0115Q2KZK8'
        message.send(msg)
        message.body['channel']=ori_channel
        message.send(msg)

        with open( config_yml ) as fy_r:
            conf = yaml.safe_load( fy_r )

        if conf['mode'] == 'single_match':
            for num_l in range( len(roundrobin) - 1 ):
                for num_r in range( num_l + 1, len(roundrobin) ):
                    dt_now_M = datetime.datetime.now().strftime('%Y%m%d%H%M')

                    matchteam = []
                    matchteam.append( roundrobin[num_l] )
                    matchteam.append( roundrobin[num_r] )

                    # with open( config_yml ) as fy_r:
                    #     conf = yaml.safe_load( fy_r )
                    conf['teams'] = matchteam
                    log_d=conf['log_dir'].split('/')

                    #log/a/などの様に前後に空の要素が出来るときの処理
                    for i in range( log_d.count("") ):
                        log_d.remove("")

                    conf['log_dir']=""
                    find_g=[ s for s in log_d if "group" in s ]
                    if len(find_g) > 0:
                        for n in range(len(log_d)):
                            if "group" in log_d[n]:
                                break
                            conf['log_dir']=conf['log_dir']+log_d[n]+'/'
                    else:
                        for n in range(len(log_d)):
                            conf['log_dir']=conf['log_dir']+log_d[n]+'/'
                    conf['log_dir']=conf['log_dir']+group+'/'+dt_now_M

                    with open( config_yml, 'w' ) as fy_w:
                        yaml.dump( conf, fy_w, default_flow_style=False )
                    msg = 'match start' + str(matchteam)
                    message.send(msg)

                    subprocess.run([tournament_path + 'start.sh', '--config='+config])

                    arg=[]
                    arg.append(tournament_path)
                    arg.append(conf['log_dir'])
                    arg.extend(roundrobin)
                    arg = " ".join(arg)
                    result = subprocess.run( ['../gametools/results/result.sh', str(arg)] )

                    rank = subprocess.run(['../gametools/results/rank.sh', str(group)], encoding='utf-8', stdout=subprocess.PIPE )
                    print(rank.stdout)
                    #standing.main(group)

                    msg = 'match finish' + str(matchteam)
                    message.send(msg)

        elif conf['mode'] == 'group':
            dt_now_M = datetime.datetime.now().strftime('%Y%m%d%H%M')
            conf['teams'] = roundrobin

            log_d=conf['log_dir'].split('/')
            #log/a/などの様に前後に空の要素が出来るときの処理
            for i in range( log_d.count("") ):
                log_d.remove("")

            conf['log_dir']=""
            find_g=[ s for s in log_d if "group" in s ]
            if len(find_g) > 0:
                for n in range(len(log_d)):
                    if "group" in log_d[n]:
                        break
                    conf['log_dir']=conf['log_dir']+log_d[n]+'/'
            else:
                for n in range(len(log_d)):
                    conf['log_dir']=conf['log_dir']+log_d[n]+'/'
            conf['log_dir']=conf['log_dir']+group+'/'+dt_now_M

            with open( config_yml, 'w' ) as fy_w:
                yaml.dump( conf, fy_w, default_flow_style=False )

            subprocess.run([tournament_path + 'start.sh', '--config='+config])

        dt_finish = datetime.datetime.now().strftime('%Y%m%d%H%M')
        msg = 'The ' + group + ' finish! \n Finish time : '+ dt_finish
        message.send(msg)
        game_flag=False
    else:
        message.send("do not start a game while other game")

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
    if message.body['user'] == organizer_id: #organizer's id
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
    if message.body['user'] == organizer_id: #organizer's id
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
    if message.body['user'] == organizer_id: #organizer's id
        global game_flag
        game_flag = False
        msg = 'enable to start a game'
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
    if bin_flag == True and list_flag == True and not game_flag:
        game_flag=True
        teamname = message.body['text']
        teamname =  ''.join(teamname[4:])
        print("test teamname:",teamname)
        file_types = ['tar.gz']
        download_file = dl.DownloadFile(file_types, home)
        result = download_file.exe_download(message._body['files'][0])
        print("bin download ",result)
        if result == 'ok':
            msg = 'binary upload complete'
            ori_channel=message.body['channel']
            message.body['channel']='C013QBT5L4R'
            message.send(msg)
            message.body['channel']=ori_channel
            message.send(msg)
        elif result == 'file type is not applicable.':
            message.send('ファイルのタイプがアップロード対象外です')
        else:
            message.send('ファイルのアップロードに失敗しました')

        sleep(5)
        subprocess.run(['../../test/extend.sh', teamname])
        message.send('binary test start (please wait approx. 1 min.)')

        teamdir = home + teamname
        teamfiles = os.listdir( teamdir )
        if "start" not in teamfiles:
            message.send("no start")
        if "kill" not in teamfiles:
            message.send("no kill")
        if "team.yml" not in teamfiles:
            ty_dict={ "country": teamname }
            with open( teamdir+"/team.yml", 'w' ) as ty_w:
                yaml.dump( ty_dict, ty_w, default_flow_style=False )
        for excecuted in teamfiles:
            os.chmod(teamdir+"/"+excecuted, 0o777)

        test_result = subprocess.run(['../../test/autotest.sh', teamname], encoding='utf-8', stdout=subprocess.PIPE )
        message.send('binary test finish')
        discon_index = test_result.stdout.find('DisconnectedPlayer')
        nl_index = test_result.stdout[discon_index:].find('\n')
        discon_p = test_result.stdout[ discon_index + len('DisconnectedPlayer'):discon_index + nl_index ]
        print('discon_p',discon_p)
        if int(discon_p) == 0:
            q_path = '../../test/qualification.txt'
            time = datetime.datetime.now().strftime('%Y%m%d%H%M')
            if os.path.exists(q_path):
                with open( q_path, 'r' ) as q_txt:
                    q_teams = q_txt.readlines()
                q_teams_row = "".join(q_teams)
                if teamname not in q_teams_row:
                    with open( q_path, 'a+' ) as q_txt_ad:
                        q_txt_ad.writelines(teamname+','+time+'\n')
                else:
                    mod_q=[]
                    for line in q_teams:
                        if teamname in line:
                            line=teamname+','+time+'\n'
                            mod_q.append(line)
                        else:
                            mod_q.append(line)
                    with open( q_path, 'w' ) as q_txt_ad:
                        q_txt_ad.writelines(mod_q)
            else:
                with open( q_path, 'w' ) as q_txt:
                    q_txt.writelines(teamname+','+time+'\n')
            msg = 'binary test complete'
            ori_channel=message.body['channel']
            message.body['channel']='C013QBT5L4R'
            message.send(msg)
            message.body['channel']=ori_channel
            message.send(msg)
        elif int(discon_p) > 0:
            message.send('disconnected player(s) ' + discon_p)
        else:
            message.send('test failed')
        game_flag=False
    elif game_flag:
        message.reply("do not start a game while other game")
    else:
        msg = 'Not allowed'
        message.reply(msg)

@respond_to('^clear qualification$')
def file_download(message):
    if message.body['user'] == organizer_id: #organizer's id
        q_path = '../../test/qualification.txt'
        if os.path.exists(q_path):
            with open( q_path, 'w' ) as q_txt:
                pass
