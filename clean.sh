#!/bin/bash

function parse_yaml () {
   local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')
   sed -ne "s|^\($s\)\($w\)$s:$s\"\(.*\)\"$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p"  $1 |
   awk -F$fs '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s=\"%s\"\n", vn, $2, $3);
      }
   }'
   return 0
}

DIR=`dirname $0`

parse_yaml ${DIR}/config/manager.yml > tmp.conf
source tmp.conf

echo "clean..."
rm tmp.conf
rm -r ${teams_dir}
rm -r ${log_dir}
rm -r ${competition_manager_path}qualified_team
rm -r ${competition_manager_path}uploaded_team
rm -r ${competition_manager_path}failed_team
rm ${competition_manager_path}config/group.yml
rm ${competition_manager_path}config/maillist.txt
rm ${competition_manager_path}config/match_list.yml
rm ${competition_manager_path}config/qualification.txt
rm ${competition_manager_path}config/qualification_test.yml
rm ${competition_manager_path}config/tournament.yml
