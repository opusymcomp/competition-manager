# -*- coding:utf-8 -*-
import os
import json
import gspread
import sys
import subprocess

from oauth2client.service_account import ServiceAccountCredentials

# teams=sys.argv
# del teams[0]
# teamDicts=[]
# for team in teams:
#     teamDict = {
#         'name' : str(team),
#         'livepts' : 0,
#         'goaldif' : 0,
#         'score' : 0,
#         'rank': 0
#     }

#     teamDicts.append( teamDict )
teamDicts=[]
path = os.path.expanduser(os.path.dirname(__file__)+"/PATH.json") # set json file
doc_id = 'DOC_ID' # doc id of google spread sheet

def main( group ):

    cmd = ("cat ../../../tournament/config/group/" +group+ ".txt")
    teams = resCmd(cmd).decode('utf-8').strip().split(",")
    #teams=sys.argv

    for team in teams:
        teamDict = {
            'name' : str(team),
            'livepts' : 0,
            'goaldif' : 0,
            'score' : 0,
            'rank': 0
        }
        teamDicts.append( teamDict )

    worksheet = readWorkSheet("test")

    row_info = worksheet.row_values( 1 )
    left_info = []
    right_info = []
    for info in row_info:
        if str( info ).find("left"):
            left_info.append( info )
        elif str( info ).find("right"):
            right_info.append( info )
    allGameResults = worksheet.get_all_records()
    gameresults = [ gameresult for gameresult in allGameResults if gameresult['left_team'] in teams and gameresult['right_team'] in teams ]

    calcRank( gameresults, left_info, right_info )

    orderedByRank( gameresults )

    resultbook = getWorkBook()
    sheettitles=[t.title for t in resultbook.worksheets()]
    if "rank_"+group not in sheettitles:
        resultbook.add_worksheet( title="rank_"+group, rows=50, cols=50 )
        headlist=["rank","name","live points","tied teams"]
        ranksheet=readWorkSheet( "rank_"+group )
        cell_list = ranksheet.range( chr(65) + '1:' + chr( 65+len(headlist)-1 ) + '1' )
        for i,cell in enumerate(cell_list):
            cell.value = headlist[i]
        ranksheet.update_cells(cell_list)
    else:
        ranksheet = readWorkSheet("rank_"+group)

    cell_list = ranksheet.range( 'A2:A' + str( len(teamDicts) + 1 ) )
    for i,cell in enumerate(cell_list):
        cell.value = teamDicts[i]['rank'] + 1
    ranksheet.update_cells(cell_list)

    cell_list = ranksheet.range( 'B2:B' + str( len(teamDicts) + 1 ) )
    for i,cell in enumerate(cell_list):
        cell.value = teamDicts[i]['name']
    ranksheet.update_cells(cell_list)

    cell_list = ranksheet.range( 'C2:C' + str( len(teamDicts) + 1 ) )
    for i,cell in enumerate(cell_list):
        cell.value = teamDicts[i]['livepts']
    ranksheet.update_cells(cell_list)

    for cell_len in range( len(teams) ):
        cell_list = ranksheet.range( chr(65+cell_len+3)+'2:'+chr(65+cell_len+3) + str( cell_len + 1 ) )
        for i,cell in enumerate(cell_list):
            cell.value = ""
        ranksheet.update_cells(cell_list)

    tiedGroup = findTiedTeams()
    for tiedT in range( len(tiedGroup) ):
        cell_list = ranksheet.range( chr(65+tiedT+3)+'2:'+chr(65+tiedT+3) + str( len(tiedGroup[tiedT]) + 1 ) )
        for i,cell in enumerate(cell_list):
            cell.value = tiedGroup[tiedT][i]['name']
        ranksheet.update_cells(cell_list)

def getWorkBook():
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
    client = gspread.authorize( credentials )

    return client.open_by_key( doc_id )

def readWorkSheet( name ):

    gfile   = getWorkBook()
    return gfile.worksheet( name ) # choose your worksheet


def calcRank( gameresults, left_info, right_info ):
    for i in range( len(teamDicts) ):
        for line in range( len(gameresults) ):
            if gameresults[line]['left_team'] == teamDicts[i]['name']:
                teamDicts[i]['livepts'] += calcLivePts( gameresults[line]['left_score'],
                                                        gameresults[line]['right_score'] )
                teamDicts[i]['goaldif'] += gameresults[line]['left_score'] - gameresults[line]['right_score']
                teamDicts[i]['score'] += gameresults[line]['left_score']
            elif gameresults[line]['right_team'] == teamDicts[i]['name']:
                teamDicts[i]['livepts'] += calcLivePts( gameresults[line]['right_score'],
                                                        gameresults[line]['left_score'] )
                teamDicts[i]['goaldif'] += gameresults[line]['right_score'] - gameresults[line]['left_score']
                teamDicts[i]['score'] += gameresults[line]['right_score']


def calcLivePts( t_score, score ):
    if t_score > score:
        return 3
    elif t_score == score:
        return 1
    elif t_score < score:
        return 0



def orderedByRank( gameresults ):
    #live points
    teamDicts.sort( key=lambda x: x['livepts'], reverse=True )
    for rank in range( len(teamDicts) - 1 ):
        if teamDicts[rank]['livepts'] > teamDicts[rank+1]['livepts']:
            teamDicts[rank+1]['rank'] = rank+1
        else:
            teamDicts[rank+1]['rank'] = teamDicts[rank]['rank']
    # print("livepts")
    # print( teamDicts )

    tiedGroup = findTiedTeams()

    for tied_ts in tiedGroup:
        tiedGames = findTiedGames( tied_ts, gameresults )

        for tiedgame in tiedGames:
            if tiedgame['left_score'] > tiedgame['right_score']:
                for tied_t in tied_ts:
                    if tied_t['name'] == tiedgame['left_team']:
                        tied_t['rank'] = tied_t['rank'] + 1
            elif tiedgame['right_score'] > tiedgame['left_score']:
                for tied_t in tied_ts:
                    if tied_t['name'] == tiedgame['right_team']:
                        tied_t['rank'] = tied_t['rank'] + 1


        pre_len = len( tied_ts )
        for tied_t in tied_ts:
            if tied_t['rank'] == len( tied_ts ) - 1:
                tied_ts.remove( tied_t )
                break
        if pre_len > len( tied_ts ):
            for tied_t in tied_ts:
                for i in range( len(teamDicts) ):
                    if teamDicts[i]['name'] == tied_t['name']:
                        teamDicts[i]['rank'] += 1


    teamDicts.sort( key=lambda x: x['rank'], reverse=False )

    # print("tie_face_to_face")
    # print( teamDicts )

    tiedGroup = findTiedTeams()

    #goal diff
    for tied_ts in tiedGroup:
        tied_i = next( (index for ( index, d ) in enumerate(teamDicts) if d['name'] == tied_ts[0]['name']), None)
        teamDicts[tied_i:tied_i+len(tied_ts)] = sorted( teamDicts[tied_i:tied_i+len(tied_ts)], key=lambda x: x['goaldif'], reverse=True )
        for rank in range( tied_i, tied_i + len(tied_ts) - 1 ):
            if teamDicts[rank]['goaldif'] > teamDicts[rank+1]['goaldif']:
                teamDicts[rank+1]['rank'] = rank+1
            else:
                teamDicts[rank+1]['rank'] = teamDicts[rank]['rank']


    # print("goaldif")
    # print( teamDicts )
    for tied_ts in tiedGroup:
        if len( tied_ts ) > 2:
            tiedGames = findTiedGames( tied_ts, gameresults )

            tied_i = next( (index for ( index, d ) in enumerate(teamDicts) if d['name'] == tied_ts[0]['name']), None)
            for tiedgame in tiedGames:
                for tied_t in tied_ts:
                    if tied_t['name'] == tiedgame['left_team']:
                        tied_t['rank'] += tiedgame['left_score'] - tiedgame['right_score']
                    elif tied_t['name'] == tiedgame['right_team']:
                        tied_t['rank'] += tiedgame['right_score'] - tiedgame['left_score']
            tied_ts.sort( key=lambda x: x['rank'], reverse=True )
            pre_rank = tied_i
            for rank in range( len(tied_ts) - 1 ):
                for t in range( tied_i, tied_i + len(tied_ts) ):
                    if teamDicts[t]['name'] == tied_ts[rank+1]['name']:
                        if tied_ts[rank]['rank'] > tied_ts[rank+1]['rank']:
                            teamDicts[t]['rank'] = rank + tied_i + 1
                            pre_rank = teamDicts[t]['rank']
                            break
                        else:
                            teamDicts[t]['rank'] = pre_rank
                            break



    teamDicts.sort( key=lambda x: x['rank'], reverse=False )

    # print("goaldif_ftof")
    # print( teamDicts )

    tiedGroup = findTiedTeams()



    #score
    for tied_ts in tiedGroup:
        tied_i = next( (index for ( index, d ) in enumerate(teamDicts) if d['name'] == tied_ts[0]['name']), None)
        teamDicts[tied_i:tied_i+len(tied_ts)] = sorted( teamDicts[tied_i:tied_i+len(tied_ts)], key=lambda x: x['score'], reverse=True )
        for rank in range( tied_i, tied_i + len(tied_ts) - 1 ):
            if teamDicts[rank]['score'] > teamDicts[rank+1]['score']:
                teamDicts[rank+1]['rank'] = rank+1
            else:
                teamDicts[rank+1]['rank'] = teamDicts[rank]['rank']


    # print("score")
    # print( teamDicts )

    tiedGroup = findTiedTeams()

    for tied_ts in tiedGroup:
        if len( tied_ts ) > 2:
            tiedGames = findTiedGames( tied_ts, gameresults )


            tied_i = next( (index for ( index, d ) in enumerate(teamDicts) if d['name'] == tied_ts[0]['name']), None)
            for tiedgame in tiedGames:
                for tied_t in tied_ts:
                    if tied_t['name'] == tiedgame['left_team']:
                        tied_t['rank'] += tiedgame['left_score']
                    elif tied_t['name'] == tiedgame['right_team']:
                        tied_t['rank'] += tiedgame['right_score']
            tied_ts.sort( key=lambda x: x['rank'], reverse=True )
            pre_rank = tied_i
            for rank in range( len(tied_ts) - 1 ):
                for t in range( tied_i, tied_i + len(tied_ts) ):
                    if teamDicts[t]['name'] == tied_ts[rank+1]['name']:
                        if tied_ts[rank]['rank'] > tied_ts[rank+1]['rank']:
                            teamDicts[t]['rank'] = rank + tied_i + 1
                            pre_rank = teamDicts[t]['rank']
                            break
                        else:
                            teamDicts[t]['rank'] = pre_rank
                            break
    # print("score_ftof")
    # print( teamDicts )




def findTiedGames( tiedteams, gameresults ):
    tiedGames = []
    for line in range( len(gameresults) ):
        for t in range( len(tiedteams) - 1 ):
            if tiedteams[t]['name'] == gameresults[line]['left_team'] or tiedteams[t]['name'] == gameresults[line]['right_team']:
                for other_t in range( t+1, len(tiedteams) ):
                    if tiedteams[other_t]['name'] == gameresults[line]['left_team'] or tiedteams[other_t]['name'] == gameresults[line]['right_team']:
                        tiedGames.append( gameresults[line] )
    return tiedGames

def findTiedTeams():
    tiedGroup = []
    pre_j = 0
    for i in range( len(teamDicts) - 1 ):
        if i < pre_j:
            continue
        if teamDicts[i]['rank'] == teamDicts[i+1]['rank']:
            tiedTeams = []
            tiedTeam = {
                'name' : str( teamDicts[i]['name'] ),
                'rank' : 0
            }
            tiedTeams.append( tiedTeam )
            for j in range( i+1, len(teamDicts) ):
                if teamDicts[i]['rank'] < teamDicts[j]['rank']:
                    break
                else:
                    tiedTeam = {
                        'name' : str( teamDicts[j]['name'] ),
                        'rank' : 0
                    }
                    tiedTeams.append( tiedTeam )
            tiedGroup.append( tiedTeams )
            pre_j = j
    return tiedGroup

def resCmd(cmd):
  return subprocess.Popen(
      cmd, stdout=subprocess.PIPE,
      shell=True).communicate()[0]

if __name__ == '__main__':
    group = sys.argv[1]
    main(group)
