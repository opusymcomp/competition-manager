# -*- coding: utf-8 -*-
import numpy as np
import itertools
import ggssapi_gameresult
import sys
import os


lineCount = 0
logpath=sys.argv[1]
#"../log/test/write/"
for f in os.listdir(logpath):
    if "csv" in f and "kick_sequence" not in f:
        for line in open( logpath+f, "r" ):
            lineCount += 1
            if lineCount == 1:
                line_info = line.split("\n")[0].split(",")
            else:
                game_result = line.split("\n")[0].split(",")
        result_dict = {}
        for i in range( len(line_info) ):
            result_dict[ str(line_info[i]) ] = game_result[i]
    # if str( line_info[i] ).find("team"):
    #     result_dict[ str(line_info[i]) ] = game_result[i]
    # else:
    #     result_dict[ str(line_info[i]) ] = int( game_result[i] )


ggssapi_gameresult.main(
    result_dict["date"],
    result_dict["our_team"],
    result_dict["opp_team"],
    result_dict["our_final_team_point"],
    result_dict["opp_final_team_point"]
)
