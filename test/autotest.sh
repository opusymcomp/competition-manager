#!/bin/bash

cd `dirname $0`
CDIR=$(cd ../; pwd)

#export PATH=${CDIR}/loganalyzer3:$PATH
#export PATH=$HOME/tool/anaconda3/bin:$PATH

SH_DIR=$(pwd)

LTEAM=$1

# team name
TEAM_L="$HOME/${LTEAM}/start.sh "
echo ${CDIR}
TEAM_R="${CDIR}/agent2d-3.1.1/src/start.sh"
#TEAM_R='"$HOME/rcss/agent2d/src/start.sh "'

LOGDIR="${CDIR}/test/log/${LTEAM}"

mkdir -p ${LOGDIR}
rm ${LOGDIR}/*


# start loop
echo "$TEAM_L"
echo "$TEAM_R"
echo "${TEAM_L} VS ${TEAM_R} : Test game start."

DATE=`date +%Y%m%d%0k%M`
rcssserver server::auto_mode = 1 \
		   server::synch_mode = false \
		   server::team_l_start = ${TEAM_L} server::team_r_start = ${TEAM_R} \
		   server::kick_off_wait = 50 \
		   server::half_time = 30 \
		   server::nr_normal_halfs = 1 server::nr_extra_halfs = 0 \
		   server::penalty_shoot_outs = 0 \
		   server::game_logging = 1 server::text_logging = 1 \
		   server::game_log_dir = "${LOGDIR}" server::text_log_dir = "${LOGDIR}" \
		   server::game_log_compression = 1 \
		   server::text_log_compression = 1 \
		   2>&1 | tee ${LOGDIR}/${DATE}.log
sleep 1
echo "${TEAM_L} VS ${TEAM_R} : Test game finished."

cd ${LOGDIR}
loganalyzer3 ${LOGDIR}/ -l
cd ${SH_DIR}

DISCONNECTED_P=`python analyze_test.py ${LOGDIR}`
echo "DisconnectedPlayer${DISCONNECTED_P}"
