# -*- coding:utf-8 -*-
import os
import json
import gspread
import sys

from oauth2client.service_account import ServiceAccountCredentials

def main( order, left_team, right_team, left_score, right_score ):
    scope = ['https://spreadsheets.google.com/feeds']
    path = os.path.expanduser(os.path.dirname(__file__)+"/PATH.json") # set json file
    doc_id = 'DOC_ID' # doc id of google spread sheet
    credentials = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
    client = gspread.authorize(credentials)
    gfile   = client.open_by_key(doc_id)
    worksheet = gfile.worksheet('test') # choose your worksheet

    column = [
        order,
        left_team,
        right_team,
        left_score,
        right_score
    ]
    #print( worksheet.get_all_records() )
    worksheet.append_row(column)
