#!/bin/bash

cd `dirname $0`
CDIR=$(cd ../../../; pwd)
GROUP=$1
python ${CDIR}/slackserver/gametools/results/standing.py ${GROUP}
