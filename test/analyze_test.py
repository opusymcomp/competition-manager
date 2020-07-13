# -*- coding: utf-8 -*-
import numpy as np
import itertools
import os
import sys
import csv

logdir = sys.argv[1]
result_dict = []
def main():
    for result in os.listdir(path=logdir):
        if "csv" in result and "kick" not in result:
            with open(logdir+"/"+result, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    print(row["our_disconnected_player"])
                    return row["our_disconnected_player"]

if __name__ == '__main__':
    main()
