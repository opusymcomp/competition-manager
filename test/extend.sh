#!/bin/bash
echo ${1}

FILENAME=${1}
TEAMS_DIR=${2}
COMPETITION_MANAGER_DIR=${3}
DIR=`dirname $0`
CDIR=`pwd`

cd $TEAMS_DIR
tar xvf $FILENAME

# back to working directory
cd ${CDIR}
