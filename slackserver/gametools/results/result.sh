#!/bin/bash

cd `dirname $0`
CDIR=$(cd ../../../; pwd)
#export PATH=${CDIR}/loganalyzer3:$PATH

#DATE=`date +%Y%m%d%0k%M`
#GROUP=$1
#LOGDIR="$HOME/competition-manager/tournament/log/test/"
#WLOG="write/"
TDIR="${CDIR}/tournament/"
#cd ${TDIR}
#echo (ls ${TDIR})
MATCH="/match_1/"
#mkdir -p ${LOGDIR}${WLOG}

IFS=" "
ARRAY=($1)
for ((i=0;i<${#ARRAY[@]};i++))
do
	# echo $i
	# TEAMS[i]=${ARRAY[i]}
	if [ $i -eq 0 ] ; then
		LOGDIR=${TDIR}${ARRAY[i]}
	else
		TEAMS[i]=${ARRAY[$((i))]}
	fi
done

cd ${LOGDIR}${MATCH}
loganalyzer3 ./ --side l

python ${CDIR}/slackserver/gametools/results/gameresult.py ./

#python ${CDIR}/slackserver/gametools/results/standing.py ${TEAMS[*]}

files=($(ls | grep rcg))
if [ ${#files[@]} -gt 0 ] ; then
	mv ./* ../
fi
