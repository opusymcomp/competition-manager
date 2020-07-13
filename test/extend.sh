#!/bin/sh
echo ${1}

cd `dirname $0`
CDIR=$(cd ../; pwd)

cd $HOME

tar zxvf ${1}.tar.gz > ${CDIR}/test/stdlog.txt
wait
cd ${CDIR}/test
sleep 5;cp start.sh ~/${1}
