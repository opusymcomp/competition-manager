#!/bin/bash
echo ${1}

cd `dirname $0`
CDIR=$(cd ../; pwd)

cd $HOME

tar xvf ${1} &> ${CDIR}/test/stdlog.txt
wait
cd ${CDIR}/test
#sleep 5;
cp start.sh ~/${1%%.*}
